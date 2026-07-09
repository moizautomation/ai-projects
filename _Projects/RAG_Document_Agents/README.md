# AI Document Intelligence Agent

An advanced RAG (Retrieval-Augmented Generation) agent that answers questions from your uploaded PDFs. It reads your documents first, and only searches the web when the answer is not in the documents. Built with a modern retrieval stack: semantic chunking, hybrid search, and cross-encoder re-ranking.

## Features

- **Multi-PDF upload** — ask questions across several documents at once
- **Semantic chunking** — splits documents by meaning, not fixed size
- **Query rewriting** — turns follow-up questions into standalone questions using chat history
- **Hybrid search** — combines keyword search (BM25) with semantic search (FAISS embeddings)
- **Cross-encoder re-ranking** — reorders retrieved chunks for better answer quality
- **Agent-based routing** — the agent decides whether to search the documents or the web
- **Conversation memory** — remembers the chat so follow-up questions make sense

## How It Works

```
question
  -> rewrite as standalone question
  -> agent decides which tool to use
       -> pdf_search: hybrid retrieval (BM25 + FAISS) -> re-rank -> top chunks
       -> web_search: fallback when the answer is not in the documents
  -> answer
```

The agent always tries the uploaded documents first. It only falls back to web search when the documents do not contain the answer or the question is about current external events.

## Tech Stack

- **LLM:** Google Gemini 2.5 Flash
- **Embeddings:** Google Gemini (models/gemini-embedding-001)
- **Re-ranker:** cross-encoder/ms-marco-MiniLM-L-6-v2 (HuggingFace)
- **Vector store:** FAISS
- **Keyword search:** BM25
- **Framework:** LangChain
- **UI:** Streamlit
- **Web search:** DuckDuckGo

## Setup

1. Clone the repository

```bash
git clone https://github.com/moizautomation/ai-projects.git
cd ai-projects
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Add your API key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_api_key_here
```

4. Run the app

```bash
streamlit run ragagent.py
```

## Usage

1. Upload one or more PDF files
2. Type your question
3. Click Enter
4. The agent reads your documents and answers, searching the web only if needed

## Notes

- The cross-encoder model downloads once on first run (a few hundred MB), then caches locally.
- Requires a Google API key for Gemini access.