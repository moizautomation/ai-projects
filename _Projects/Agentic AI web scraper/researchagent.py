from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

memory = InMemoryChatMessageHistory()

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

search = DuckDuckGoSearchRun()


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

@tool
def summarizer(clean: str) -> str:
    """Use this after scraping a webpage.
    Input should be webpage content.
    Output is a concise summary."""

    if clean is None  or len(clean.strip()) == 0:
        return ("No content available to summarize.")
    
    prompt = ChatPromptTemplate.from_template("""
    Summarize the following data while keeping the facts intact:
    {clean}
""")
    

    chain = prompt | model
    
    summary = chain.invoke({"clean" : clean})

    return summary.content

@tool
def report_generator(findings: str) -> str:
    """Use this after summarization.
    Input should be research findings or summaries.
    Output should be a structured report containing:
    Title
    Overview
    Key Findings
    Conclusion"""

    if findings is None or len(findings.strip()) == 0:
        return("No findings available for report generation.")
    
    prompt = ChatPromptTemplate.from_template("""
    Generate a report of the findings: {findings}
    follow the following format:
    Title
    Overview
    Key Findings
    Conclusion
""")

    chain = prompt | model

    report = chain.invoke(
        {
            "findings" : findings
        }
        )

    return report.content
    



tools = [web_search, web_scraper,summarizer,report_generator]

# Pull the standard ReAct prompt — has all required placeholders
prompt = ChatPromptTemplate.from_template("""
Answer the following question as best you can.
If the user asks for research,
first search,
then scrape,
then summarize,
then generate a report.
                                          
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

for i in range (0,5):
    query = input("Enter your prompt here: ")

    history = ""
    for msg in memory.messages:
        # msg.type returns 'human' or 'ai'
        speaker = "Human" if msg.type == "human" else "AI"
        history += f"{speaker}: {msg.content}\n"

    response = agent_executor.invoke(
        {
            "history" : history,
            "input": query
        }
    )

    memory.add_user_message(query)
    memory.add_ai_message(response["output"])


    print("\nFinal Answer:\n", response["output"])