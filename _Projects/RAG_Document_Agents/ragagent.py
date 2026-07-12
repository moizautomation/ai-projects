# AI DOCUMENT INTELLIGENCE AGENT
# Flow:
#   rewrite question -> hybrid retrieval (BM25 + FAISS)
#   -> re-ranking -> top 3 chunks -> agent decides tool -> answer

from fastapi.middleware.cors import CORSMiddleware
import time
from collections import defaultdict
from fastapi import Request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.agents import AgentExecutor, create_react_agent
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from typing import List
import tempfile
import os
import uuid
from dotenv import load_dotenv


# Load environment variables (API keys etc.) from .env
load_dotenv()


app = FastAPI(title="AI DOCUMENT INTELLIGENCE AGENT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELS (LLM, embeddings, cross-encoder)

# Primary LLM used for answering and the rewrite step
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

# Local embedding model used for semantic chunking + FAISS
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# Cross-encoder that scores (question, chunk) pairs for re-ranking
cross_encoder = HuggingFaceCrossEncoder(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# Wrap the cross-encoder in a re-ranker that keeps the top 3 chunks
reranker = CrossEncoderReranker(model=cross_encoder, top_n=3)


search_web = DuckDuckGoSearchRun()


# Simple in-memory rate limiter: tracks request timestamps per IP.
# Replaces slowapi (dependency conflicts on Python 3.14).
request_log = defaultdict(list)

def check_rate_limit(request, max_requests: int, window_seconds: int = 60):
    """Raises 429 if this IP has exceeded max_requests in the window."""
    ip = request.client.host
    now = time.time()

    # Drop timestamps older than the window
    request_log[ip] = [t for t in request_log[ip] if now - t < window_seconds]

    if len(request_log[ip]) >= max_requests:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    request_log[ip].append(now)

# SESSION STORE
# Streamlit used st.session_state to persist the vector db + history
# per browser session automatically. FastAPI has no such concept, so
# we keep a simple in-memory dict keyed by a session_id we hand back
# to the client after /upload. Each session holds everything that was
# previously cached in st.session_state, plus the compression_retriever
# and agent_executor built on top of it (since the pdf_search tool
# needs to close over that session's own retriever, not a global one).
sessions = {}


# PROMPTS

# Prompt that rewrites a follow-up question into a standalone question
rewrite_prompt = ChatPromptTemplate.from_template("""
Given the conversation history and the follow-up question, 
rewrite the follow-up question as a standalone complete question.

Conversation History:
{history}

Follow-up Question:
{question}

Standalone Question:
""")

# ReAct agent prompt — has all required placeholders
# (tools, tool_names, input, agent_scratchpad)
promptt = ChatPromptTemplate.from_template("""
                                           
IMPORTANT STRATEGY:
Always use pdf_search FIRST to look in the user's uploaded documents.
Only use web_search if pdf_search does not contain the answer,
or if the question is clearly about current external events
not found in the documents.

CITATION RULE:
Every tool result you receive is tagged with its source (either a PDF
filename + page number, or "Web Search"). When you give the Final Answer,
mention which source(s) the information came from, using those exact tags.
                                                                                
Here is the previous conversation history:
{history}
You have access to the following tools:

{tools}

Use this format:

Question: the input question you must answer

Thought: you should always think about what to do

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

... (this Thought/Action/Action Input/Observation can repeat N times)

Thought: I now know the final answer

Final Answer: the final answer to the original question

Question: {input}

Thought: {agent_scratchpad}
                                          
""")

# Chain that rewrites the follow-up question into a standalone one
rewrite_chain = rewrite_prompt | model | StrOutputParser()


def build_tools_for_session(compression_retriever):
    """Builds the pdf_search + web_search tools bound to one session's
    own compression_retriever. This replaces the old global @tool
    functions, since each session now has its own vector db and we
    can't let sessions share one retriever."""

    @tool
    def pdf_search(query: str) -> str:
        """PRIMARY tool. Always search here FIRST for any question.
        Searches the user's uploaded documents, which are the main
        knowledge base. Use this before trying anything else."""
        # Run the full pipeline (hybrid retrieval + re-rank) and return chunk text
        docs = compression_retriever.invoke(query)

        # Tag each chunk with its source filename + page number so the
        # agent can cite exactly where the answer came from
        labeled_chunks = []
        for d in docs:
            source = d.metadata.get("source", "unknown file")
            page = d.metadata.get("page")
            page_label = f", page {page + 1}" if page is not None else ""
            labeled_chunks.append(f"[Source: {source}{page_label}]\n{d.page_content}")

        return "\n\n".join(labeled_chunks)

    @tool
    def web_search(query: str) -> str:
        """FALLBACK tool. Only use this if pdf_search did NOT contain
        the answer, or if the question is clearly about current external
        events not in the uploaded documents."""

        result = search_web.run(query)

        # Return the result only if the search actually returned something,
        # tagged so the agent knows this came from the web, not the PDFs
        if result is not None and len(result) != 0:
            return f"[Source: Web Search]\n{result}"

        return None

    # List of tools the agent has access to
    return [pdf_search, web_search]


@app.post("/upload")
async def upload_pdfs(request: Request, files: List[UploadFile] = File(...)):
    """Replaces the Streamlit file_uploader block. Loads the PDFs,
    builds the semantic chunks + hybrid retriever + agent for a new
    session, and returns a session_id the client uses in /ask."""

    check_rate_limit(request, max_requests=5, window_seconds=60)

    # Stop early if no file was uploaded
    if not files:
        raise HTTPException(status_code=400, detail="No File Uploaded")

    # LOAD PDFS -> DOCUMENTS
    documents = []
    names = []

    for file in files:

        try:
            # Write the uploaded file to a temp file so PyPDFLoader can read it
            content = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                temp.write(content)
                temp_path = temp.name
                names.append(file.filename)

            # Load the PDF into Document objects
            loader = PyPDFLoader(temp_path)
            docs = loader.load()

            # Overwrite the temp path with the real filename for clean citations
            for doc in docs:
                doc.metadata["source"] = file.filename

            # Add this file's pages into the master documents list
            documents.extend(docs)

        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=500, detail=str(e))

        # Clean up the temp file now that its data is in memory
        os.remove(temp_path)

    # Guard against empty PDFs
    if documents is None or len(documents) == 0:
        raise HTTPException(status_code=400, detail="The PDF Have no data")

    # CHUNKING + VECTOR STORE

    # Split into semantic chunks (splits when topic shifts past a threshold)
    # Built every run so BM25 always has chunks available
    splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile"
    )
    semantic_chunks = splitter.split_documents(documents)

    # Build the vector DB for this session
    vector_db = FAISS.from_documents(
        documents=semantic_chunks,
        embedding=embeddings
    )

    # RETRIEVERS: semantic + keyword -> hybrid -> re-rank

    # Semantic (embedding) retriever from FAISS
    semantic_retriever = vector_db.as_retriever(
        search_kwargs={"k": 5}
    )

    # Keyword (exact match) retriever using BM25 over the same chunks
    keyword_retriever = BM25Retriever.from_documents(semantic_chunks)
    keyword_retriever.k = 5

    # Combine keyword + semantic results into one hybrid retriever
    hybrid_search = EnsembleRetriever(
        retrievers=[keyword_retriever, semantic_retriever],
        weights=[0.4, 0.6]
    )

    # Wrap hybrid retriever so its results pass through the re-ranker
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=hybrid_search
    )

    # AGENT + CHAINS

    tools = build_tools_for_session(compression_retriever)

    # Build the ReAct agent from model + tools + prompt
    agent = create_react_agent(model, tools, promptt)

    # Executor that actually runs the think -> act -> observe loop
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    # Create + store this session (replaces st.session_state.vector / .names / .history)
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "vector": vector_db,
        "names": names,
        "history": [],
        "compression_retriever": compression_retriever,
        "agent_executor": agent_executor,
    }

    return {"session_id": session_id, "files_loaded": names}


@app.post("/ask")
async def ask_question(request: Request, session_id: str = Form(...), question: str = Form(...)):    
    """Replaces the Streamlit question input + button block. Rewrites
    the question, runs the agent, updates history, returns the answer."""

    check_rate_limit(request, max_requests=15, window_seconds=60)

    # Stop early if there is no question yet
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")

    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found. Upload PDFs first via /upload")

    # Flatten stored history into a single string
    history = "\n".join(session["history"])

    # Turn the follow-up question into a standalone question
    standalone_question = rewrite_chain.invoke({
        "history": history,
        "question": question
    })

    # Let the agent decide which tool(s) to use and produce the answer
    final_res = session["agent_executor"].invoke(
        {
            "input": standalone_question,
            "history": history
        }
    )

    # Save both turns to history
    session["history"].append(f"Human: {question}")
    session["history"].append(f"AI: {final_res['output']}")

    # Return the answer
    return {"answer": final_res["output"]}