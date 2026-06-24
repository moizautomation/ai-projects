from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

search = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """Perform a web search for the given query"""
    return search.run(query)

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

    return cleaned


tools = [web_search, web_scraper]


# Pull the standard ReAct prompt — has all required placeholders
prompt = ChatPromptTemplate.from_template("""
Answer the following question as best you can.

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


agent = create_react_agent(
    model,
    tools, 
    prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools, 
    verbose=True,
    handle_parsing_errors=True
)

query = input("Enter your prompt here: ")

response = agent_executor.invoke({"input": query})

print("\nFinal Answer:\n", response["output"])