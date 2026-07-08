from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

st.title("AI DOCUMENT INTELLIGENCE AGENT")
st.divider()

model = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/gemini-embedding-001"
# )

st.subheader("Upload PDF")
files = st.file_uploader("Choose Files",type="pdf",accept_multiple_files=True)

st.subheader("Ask Your Question")
question = st.text_input("Enter your Question")

button = st.button("Enter")

if not question:
    st.stop()

if not files:
    st.error("No File Uploaded")
    st.stop()

documents = []

names = []
for file in files:
    
    try:

        with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as temp:

            temp.write(file.getvalue())

            temp_path = temp.name

            names.append(file.name)

        loader = PyPDFLoader(temp_path)

        docs = loader.load()

        documents.extend(docs)

    except Exception as e:
        print(str(e))
        st.stop()

with st.spinner("Readin the PDF"):
    if documents is None or len(documents) == 0 :
        st.error("The PDF Have no data")
        st.stop()

    if "history" not in st.session_state:
        st.session_state.history = []

    if "names" not in st.session_state:
        st.session_state.names = ""
    
    else:
        if st.session_state.names != names and "vector" in st.session_state:
            del st.session_state.vector
    #st.session_state safe value of its variable
    # the same after every rerun
    # if the variable is not made
    if "vector" not in st.session_state:

        # will split only when a change in topic above a 
        # threshold is detected
        splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile"   
        )

        chunks = splitter.split_documents(documents)

        vector_db = FAISS.from_documents(
            documents = chunks,
            embedding = embeddings
        )

        # assign the variable the vector database
        st.session_state.vector = vector_db

        st.session_state.names = names
    # if variable is already been made
    else:

        # take the value and assign it to your local variable
        vector_db = st.session_state.vector
    

retriever = vector_db.as_retriever(
    search_kwargs={"k":3}
)


prompt = ChatPromptTemplate.from_template("""
Answer the following question using ONLY the provided context.

Conversation History:
{history}
                                          
Context:
{context}

Question:
{question}

If the answer is not present in the context, say:
"I don't know."

Answer:
""")

rewrite_prompt = ChatPromptTemplate.from_template("""
Given the conversation history and the follow-up question, 
rewrite the follow-up question as a standalone complete question.

Conversation History:
{history}

Follow-up Question:
{question}

Standalone Question:
""")

rewrite_chain = rewrite_prompt | model | StrOutputParser()


rag_chain = (
    {
        # lambda men take only the question from the dictionary
        "context": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"],
        "history": lambda x: x["history"]
    }
    | prompt
    | model
    # return only the final answer
    | StrOutputParser()
)

if button:
    history = "\n".join(st.session_state.history)

    standalone_question = rewrite_chain.invoke({
    "history": history,
    "question": question
    })

    result = rag_chain.invoke(
        {
            "question" : standalone_question,
            "history" : history
        }
    )

    st.session_state.history.append(f"Human: {question}")
    st.session_state.history.append(f"AI: {result}")

    # skips the LLM entirely, just fetches the matching chunks directly
    docs = retriever.invoke(question)

    st.subheader("Answer")
    st.write(result)

    st.subheader("Sources")

    if "I don't know" not in result:
        for i, doc in enumerate(docs, start=1):
            with st.expander(f"Source {i} — Page {doc.metadata.get('page', 'N/A')}"):
                st.write(f"**File:** {doc.metadata.get('source', 'Unknown')}")
                st.write(doc.page_content)