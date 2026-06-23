from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup
import os
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
    """Scrape the data of the website"""
    cleaned = ""
    if (url.startswith("http://") or url.startswith("https://")):
        try:
            r = requests.get(url)
            if r.status_code != 200:
                    return (f"Website {url} cannot be reached Error: {r.status_code}")

            
            soup = BeautifulSoup(r.text,"html.parser")

            data = soup.find_all(["h1","h2","h3","h4","h5","h6","p"])
                    
            for el in data:
                cleaned += el.text.strip() + "\n"

        except Exception as e:   
            return str(e)
    else:
         return ("Invalid URL Provided")
    return cleaned


query = input("Enter your Prompt here: ")

model_with_tools = model.bind_tools([web_search,web_scraper])

response = model_with_tools.invoke(query)

tools_map = {
    "web_search" : web_search,
    "web_scraper" : web_scraper
}
results = []
for tools_call in response.tool_calls:
    tool_name = tools_call["name"]
    tool_args = tools_call["args"]
    result = tools_map[tool_name].invoke(tool_args)

    results.append(f"{tool_name} returned: {result}")

result = "\n".join(results)

prompt = ChatPromptTemplate.from_template("""
    Here is the result of the web search : {result}
    Answer the following query of the User: {query}
""")

chain = prompt | model

final_result = chain.invoke(
    {
        "result" : results,
        "query" : query
    }
)

print("Final Result: ",final_result.content)