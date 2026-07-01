from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.title("AI DOCUMENT INTELLIGENCE AGENT")
st.divider()

model = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

st.subheader("Upload PDF")
files = st.file_uploader("Choose Files",type="pdf",accept_multiple_files=True)

if not files:
    st.error("No File Uploaded")
    st.stop()

documents = []

for file in files:
    
    try:
        loader = PyPDFLoader(file)
        documents += loader.load()
    except Exception as e:
        print(str(e))
        st.stop()

with st.spinner("Readin the PDF"):
    if documents is None or len(documents) == 0 :
        st.error("The PDF Have no data")
        st.stop()

    splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,

    chunk_overlap = 200    
    )

    chunks = splitter.split_documents(documents)

    vector_db = FAISS.from_documents(
            documents = chunks,
            embedding = embeddings
    )

retriever = vector_db.as_retriever(
    search_kwargs={"k":3}
)

st.subheader("Ask Your Question")
question = st.text_input("Enter your Question")

if not question:
    st.error("The question cannot be empty")
    st.stop()

prompt = ChatPromptTemplate.from_template("""
Answer the following question using ONLY the provided context.

Context:
{context}

Question:
{question}

If the answer is not present in the context, say:
"I don't know."

Answer:
""")

rag_chain = (
    {
        "context" : retriever,
        "question" : RunnablePassthrough()
    }
    | prompt
    | model 
    | StrOutputParser()
)

result = rag_chain.invoke(question)

st.subheader("Answer")
st.write(result)

st.text("Sources")

docs = retriever.invoke(question)

for i, doc in enumerate(docs, start=1):
    st.write("="*50)
    st.write(f"Source {i}")
    st.write(doc.metadata)
    st.write(doc.page_content)