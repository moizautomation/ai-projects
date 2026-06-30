from langgraph.graph import StateGraph,END
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage,ToolMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


SYSTEM_INSTRUCTIONS = """
You are an AI Research Agent.

Your only responsibility is to collect accurate research.

You have access to two tools:

1. web_search(query)
   - Do web_search maximum of 2 times
   - Use this to search for companies, topics, or websites.

2. web_scraper(url)
   - Scrape website maximum of 1 time
   - Use this after you have a website URL and need detailed information.

Rules:

- Never make up facts.
- Never hallucinate.
- Never answer from memory if a tool can provide the information.
- If more information is required, call the appropriate tool.
- You may call multiple tools if necessary.
- Continue using tools until you have enough information.
- Once enough information has been collected, stop calling tools.

Important:

- Do NOT summarize the research.
- Do NOT generate outreach ideas.
- do not invent statistics or cite studies that are not verified in the research provided
- Those are handled by later nodes.

Your job ends once all required research has been collected.
"""

search = DuckDuckGoSearchRun()

memory = MemorySaver()

class State(TypedDict):
    messages : Annotated[list, add_messages]

@tool
def web_search(query: str) -> str:
    """Use this first when researching a topic. Performs a web search and 
    Returns websites and information related to the topic."""

    result = search.run(query)
    if result is None or len(result.strip()) == 0:
        return ("No Search Result Found.")
    
    return result

@tool
def web_scraper(url: str) -> str:
    """Scrape readable text content from a webpage.
    Pass a full URL starting with http:// or https://"""
    cleaned = ""

    if url.startswith("http://") or url.startswith("https://"):
        try:
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                return f"Website {url} cannot be reached Error: {r.status_code}"

            soup = BeautifulSoup(r.text, "html.parser")

            data = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"])

            for el in data:
                cleaned += el.text.strip() + "\n"

        except Exception as e:
            return str(e)
    else:
        return "Invalid URL Provided"

    if len(cleaned) == 0:
        return ("No headings or paragraphs found on page.")
    
    return cleaned[:3000]


def summarizer(clean: str) -> str:
    prompt = ChatPromptTemplate.from_template("""
You are an expert research analyst.

Summarize the following research into:

- Company / Topic Overview
- Main Products or Services
- Important Technologies
- Interesting Facts

Research:

{data}
""")

    chain = prompt | model

    response = chain.invoke(
        {
            "data": clean
        }
    )

    return response.content


def outreach_generator(findings: str) -> str:
    prompt = ChatPromptTemplate.from_template("""
You are a sales strategist.

Based on this research generate exactly three outreach ideas.

For each one provide:

Title

Explanation

Why it may work

Research

{research}
""")

    chain = prompt | model

    response = chain.invoke(
        {
            "research": findings
        }
    )

    return response.content

def summary(state):
    research = []

    for msg in state["messages"]:

        if isinstance(msg, ToolMessage):

            if msg.content.strip():
                
                research.append(msg.content)

    combined_research = "\n\n".join(research)

    response = summarizer(clean=combined_research)

    if "Invalid URL" in response:
        return {
            "messages":[AIMessage(content="Unable to scrape website.")]
        }

    return {
        "messages": [AIMessage(content=response)]
    }

def outreach(state):

    summary = state["messages"][-1].content

    response = outreach_generator(findings=summary)

    final_report = f"""
==============================
AI RESEARCH REPORT
==============================

Research Summary

{summary}

==============================

Outreach Angle Suggestions

{response}

==============================
"""

    return {
        "messages":[AIMessage(content=final_report)]
    }

def chatbot(state):
    messages = [
    SystemMessage(content=SYSTEM_INSTRUCTIONS),
    # it means instead of creating a nested list insert all elements from below list in this list
    *state["messages"]
]

    response = model_with_tools.invoke(messages)

    return {
        "messages" : [response]
    }

def should_continue(state):
    
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools_node"
    
    return "summarize"

tools = [web_search,web_scraper]


tools_node = ToolNode(tools)

model_with_tools = model.bind_tools(tools)

# Graph Flow
#
# User
#   ↓
# Chatbot
#   ↓
# ToolNode (Search / Scrape)
#   ↓
# Chatbot
#   ↓
# Summary
#   ↓
# Outreach
#   ↓
# Final Report
graph = StateGraph(State)

graph.add_node("chatbot",chatbot)
graph.add_node("tool_node",tools_node)
graph.add_node("summarizer_node",summary)
graph.add_node("outreach_node",outreach)

graph.set_entry_point("chatbot")


graph.add_conditional_edges(
     "chatbot",
     should_continue,
     {
        "tools_node" : "tool_node",
        "summarize": "summarizer_node"
     }
)    

graph.add_edge("tool_node","chatbot")
graph.add_edge("summarizer_node","outreach_node")
graph.add_edge("outreach_node",END)

app = graph.compile(
    checkpointer=memory
)

config = {
    "configurable": {
        "thread_id": "2"
    }
}


question = input("Enter your Prompt: ")

result = app.invoke(
    {
        "messages" : [HumanMessage(content=question)]
    },
    config = config
)

print(result["messages"][-1].content)
   
