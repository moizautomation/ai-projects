# AI DOCUMENT INTELLIGENCE AGENT
# Flow:
#   rewrite question -> hybrid retrieval (BM25 + FAISS)
#   -> re-ranking -> top 3 chunks -> agent decides tool -> answer


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
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
import streamlit as st
import tempfile
import os
from dotenv import load_dotenv


# Load environment variables (API keys etc.) from .env
load_dotenv()


st.title("AI DOCUMENT INTELLIGENCE AGENT")
st.divider()

# MODELS (LLM, embeddings, cross-encoder)

# Primary LLM used for answering and the rewrite step
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

# Local embedding model used for semantic chunking + FAISS
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/gemini-embedding-001"
# )

# Cross-encoder that scores (question, chunk) pairs for re-ranking
cross_encoder = HuggingFaceCrossEncoder(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# Wrap the cross-encoder in a re-ranker that keeps the top 3 chunks
reranker = CrossEncoderReranker(model=cross_encoder, top_n=3)



# TOOLS (the agent picks between these dynamically)

@tool
def pdf_search(query: str) -> str:
    """PRIMARY tool. Always search here FIRST for any question.
    Searches the user's uploaded documents, which are the main
    knowledge base. Use this before trying anything else."""
    # Run the full pipeline (hybrid retrieval + re-rank) and return chunk text
    docs = compression_retriever.invoke(query)
    return "\n\n".join(d.page_content for d in docs)



search_web = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """FALLBACK tool. Only use this if pdf_search did NOT contain
    the answer, or if the question is clearly about current external
    events not in the uploaded documents."""
    
    result = search_web.run(query)

    # Return the result only if the search actually returned something
    if result is not None and len(result) != 0:
        return result

    return None


# List of tools the agent has access to
tools = [pdf_search, web_search]



# FILE UPLOAD + QUESTION INPUT

st.subheader("Upload PDF")
files = st.file_uploader("Choose Files", type="pdf", accept_multiple_files=True)

st.subheader("Ask Your Question")
question = st.text_input("Enter your Question")

button = st.button("Enter")

# Stop early if there is no question yet
if not question:
    st.stop()

# Stop early if no file was uploaded
if not files:
    st.error("No File Uploaded")
    st.stop()



# LOAD PDFS -> DOCUMENTS

documents = []
names = []

for file in files:

    try:
        # Write the uploaded file to a temp file so PyPDFLoader can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(file.getvalue())
            temp_path = temp.name
            names.append(file.name)

        # Load the PDF into Document objects
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        # Overwrite the temp path with the real filename for clean citations
        for doc in docs:
            doc.metadata["source"] = file.name

        # Add this file's pages into the master documents list
        documents.extend(docs)

    except Exception as e:
        print(str(e))
        st.stop()

    # Clean up the temp file now that its data is in memory
    os.remove(temp_path)



# CHUNKING + VECTOR STORE (cached in session_state)

with st.spinner("Reading the PDF"):

    # Guard against empty PDFs
    if documents is None or len(documents) == 0:
        st.error("The PDF Have no data")
        st.stop()

    # Initialize conversation history once
    if "history" not in st.session_state:
        st.session_state.history = []

    # Track uploaded filenames; reset the vector if the files change
    if "names" not in st.session_state:
        st.session_state.names = ""
    else:
        if st.session_state.names != names and "vector" in st.session_state:
            del st.session_state.vector

    # Split into semantic chunks (splits when topic shifts past a threshold)
    # Built every run so BM25 always has chunks available
    splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile"
    )
    semantic_chunks = splitter.split_documents(documents)

    # Build the vector DB only once, then cache it in session_state
    if "vector" not in st.session_state:

        vector_db = FAISS.from_documents(
            documents=semantic_chunks,
            embedding=embeddings
        )
        # Cache the vector DB + the filenames it was built from
        st.session_state.vector = vector_db
        st.session_state.names = names

    # If already built, reuse the cached vector DB
    else:
        vector_db = st.session_state.vector



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



# AGENT + CHAINS

# Build the ReAct agent from model + tools + prompt
agent = create_react_agent(model, tools, promptt)

# Executor that actually runs the think -> act -> observe loop
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors=True)

# Chain that rewrites the follow-up question into a standalone one
rewrite_chain = rewrite_prompt | model | StrOutputParser()



# RUN ON BUTTON PRESS
if button:

    # Flatten stored history into a single string
    history = "\n".join(st.session_state.history)

    # Turn the follow-up question into a standalone question
    standalone_question = rewrite_chain.invoke({
        "history": history,
        "question": question
    })

    # Let the agent decide which tool(s) to use and produce the answer
    final_res = agent_executor.invoke(
        {
            "input": standalone_question,
            "history": history
        }
    )

    # Save both turns to history
    st.session_state.history.append(f"Human: {question}")
    st.session_state.history.append(f"AI: {final_res['output']}")

    # Display the answer
    st.subheader("Answer")
    st.write(final_res["output"])

