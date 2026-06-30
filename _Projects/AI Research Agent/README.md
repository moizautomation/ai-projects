# AI Research Agent (LangGraph)

A multi-step AI research agent built with LangGraph that researches any company or topic and generates structured outreach angles.

## How it works

1. User enters a company name or topic
2. Agent dynamically decides whether to search the web, scrape a website, or both
3. Findings are summarized into a structured report
4. Agent generates 3 outreach angles based on the research

## Architecture

```
User → Chatbot (decides tool use) → ToolNode (search/scrape) → Chatbot
                                                                    ↓
                                                          Summarizer Node
                                                                    ↓
                                                          Outreach Node
                                                                    ↓
                                                            Final Report
```

Built with `StateGraph`, conditional edges, `ToolNode`, and `MemorySaver` for persistent conversation memory.

## Tech Stack

- LangGraph
- LangChain
- Gemini 2.5 Flash
- DuckDuckGo Search
- BeautifulSoup (web scraping)

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
python businessresearch.py
```

Enter a company name or topic when prompted.

## Output

The agent returns a structured report containing:
- Company/Topic Overview
- Main Products or Services
- Important Technologies
- Interesting Facts
- 3 Outreach Angle Suggestions