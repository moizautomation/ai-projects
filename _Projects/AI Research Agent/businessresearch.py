from langgraph.graph import StateGraph,END
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

model_flash1 = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash"
)

model_flash2 = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

search = DuckDuckGoSearchRun()

memory = MemorySaver()

class State(TypedDict):
    messages : Annotated[list, add_messages]

@tool
def web_search(query: str) -> str:
    pass

@tool
def web_scraper(url: str) -> str:
    pass

@tool
def summarizer(clean: str) -> str:
    pass
@tool
def outreach_generator(findings: str) -> str:
    pass

def search(state):
    pass

def scrape(state):
    pass

def summary(state):
    pass

def outreach(state):
    pass

def chatbot(state):
    pass

def should_continue(state):
    pass

tools = [web_search,web_scraper,summarizer,outreach_generator]

model_flash1_with_tools = model_flash1.bind_tools(tools)

tools_node = ToolNode(tools)

graph = StateGraph(State)

graph.add_node("chatbot",chatbot)
graph.add_node("web_search",search)
graph.add_node("web_scraper",scrape)
graph.add_node("summarizer_node",summary)
graph.add_node("outreach_node",outreach)

graph.set_entry_point("chatbot")

graph.add_conditional_edges(
     "chatbot",
     should_continue,
     {
        "search" : "web_search",
        "scrape" : "web_scraper",
        "summary" : "summarizer_node",
        "outreach" : "outreach_node",
        END : END
     }
)

graph.add_edge("web_search",END)
graph.add_edge("web_scraper",END)
graph.add_edge("summarizer_node",END)
graph.add_edge("outreach_node",END)

app = graph.compile()

result = app.invoke(
    {
        "messages" : [HumanMessage(content="Research Python.")]
    }
)
   