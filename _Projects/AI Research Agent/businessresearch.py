from langgraph.graph import StateGraph,END
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage,AIMessage
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
Summarize the following research:

{data}
""")

    chain = prompt | model_flash1

    response = chain.invoke(
        {
            "data": clean
        }
    )

    return response.content


def outreach_generator(findings: str) -> str:
    prompt = ChatPromptTemplate.from_template("""
Generate 3 outreach angles for the following company research.

Research:
{research}
""")

    chain = prompt | model_flash2

    response = chain.invoke(
        {
            "research": findings
        }
    )

    return response.content

def summary(state):
    message = state["messages"][-1].content

    response = summarizer(clean=message)

    return {
        "messages" : [AIMessage(content=response)]
    }

def outreach(state):
    message = state["messages"][-1].content

    response = outreach_generator(findings=message)

    return {
        "messages" : [AIMessage(content=response)]
    }

def chatbot(state):
    response = model_flash1_with_tools.invoke(state["messages"])

    return {
        "messages" : [response]
    }

def should_continue(state):
    
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools_node"
    
    return END

tools = [web_search,web_scraper]


tools_node = ToolNode(tools)

model_flash1_with_tools = model_flash1.bind_tools(tools)

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
        END: "summarizer_node"
     }
)    

graph.add_edge("tool_node","chatbot")
graph.add_edge("summarizer_node","outreach_node")
graph.add_edge("outreach_node",END)

app = graph.compile()

result = app.invoke(
    {
        "messages" : [HumanMessage(content="Research Python.")]
    }
)
   
