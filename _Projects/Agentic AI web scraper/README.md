# Multi-Step Research Agent (LangChain)

A ReAct agent built with LangChain and Streamlit that researches any topic through a multi-step pipeline with live reasoning steps shown in the UI.

## How it works

1. User enters a research query in the Streamlit app
2. Agent searches the web, scrapes a relevant page, summarizes findings, and generates a structured report
3. Each reasoning step (Thought, Action, Observation) is displayed live in the UI
4. Conversation history persists across multiple queries

## Architecture

Built with `create_react_agent` and `AgentExecutor` using a custom ReAct prompt with 4 tools:

- `web_search` — searches the web via DuckDuckGo
- `web_scraper` — scrapes readable content from a webpage
- `summarizer` — summarizes scraped content
- `report_generator` — generates a structured report (Title, Overview, Key Findings, Conclusion)

A custom `ToolTracker` callback captures each tool call and displays it in the Streamlit UI.

## Tech Stack

- LangChain
- Gemini 2.5 Flash
- Streamlit
- DuckDuckGo Search
- BeautifulSoup

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
GOOGLE_API_KEY=your_gemini_api_key
```

## Run

```bash
streamlit run businessresearch.py
```

## Output

Live reasoning steps shown on the left, final structured report shown on the right.