#Lead Generation Bot Project
# Goals:
# Extract structured data
# What it should do
# Scrape product/business data
# Store in JSON
# Handle multiple pages
#send description to ai to get summary

import google.generativeai as genai
import time
import json
from dotenv import load_dotenv 
import os
import requests
from bs4 import BeautifulSoup


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#Phase 4 - Control AI output and restrict it to only give in strict JSON format
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    You must act like a strict assistant who only does what he is asked of. 
    You will receive text + mode.
    You should strictly output in the format defined below. The json format to follow is:

    If mode = Summary
    Format:
    {
    "mode": "only give mode",
    "summary": "you must give short explanation. no extra wordss"
    }

    If mode = Key Points
    Format:
    {
    "mode": "only give mode",
    "keypoints": Only give three key points["point 1","point 2","point 3"]
    }

    If mode = Sentiment
    Format:
    {
    "mode": "only give mode",
    "sentiment": "strictly give one of: positive / negative / neutral"
    } 
    """)

    
#make scraper look like a real browser instead of bot
headers = {
    "User-Agent": "Mozilla/5.0"
}
#Phase 1 - Input Validation and Mode setting
url = input("Enter the Target URL: ")
#remove unnecesary characters from the url like \n
url = url.strip()


print("1. Summary\n2. Key Points\n3. Sentiment")
choice = input("Enter the mode: ")

#if user enter string instead of number then
#we try to convert it into int
try:
    choice = int(choice)
    if(choice == 1):
        mode = "Summary"
    elif(choice == 2):
        mode = "Key Points"
    elif(choice == 3):
        mode = "Sentiment"
    else:
        mode = "Summary"  
    #if cannot be converted
    #then set default mode to summary
except:
    mode = "Summary"
user_input = url + mode

    #check if url is empty
if(len(url) == 0):
    print("Input cannot be empty")
    exit()
a = "http"
b = "https"

#check if url is valid
if a in url or b in url:
    #error handling
    try:
        #send the request to the website
        r = requests.get(url, headers = headers)
    except:
        print("Website cannot be reached")
        exit()
    
#Phase 2 - Extracting useful data from web page
#getting the html thorough beautiful soup
soup = BeautifulSoup(r.text,"html.parser")
#returns a list of all p tags
para = soup.find_all("p")

heading1 = soup.find_all("h1")
heading2 = soup.find_all("h2")
heading3 = soup.find_all("h3")

heading4 = soup.find_all("h4")
heading5 = soup.find_all("h5")
heading6 = soup.find_all("h6")

#merge all the headings text
headings = heading1 + heading2 + heading3 + heading4 + heading5 + heading6
#merge all the text
merge_data = para + headings

#Phase 3 - Sending cleaned data to AI
cleaned = ""
#cleaning the merged data by removing
#unnecassory characters and spaces
for data in merge_data:
    cleaned += " " + data.text.strip() + " \n"



prompt = f"""

Text:
{cleaned}

Mode:
{mode}

"""

data_list = []
aires = "API Failed"

#Phase 5 - Write your JSON data to a json file
with open("data.json","w") as file:
    #try to send the prompt to AI API
    try:
        response = model.generate_content(prompt)
        print(response.text)
        aires = response.text.strip()

        #add the result of that response in list
        data_list.append({
        "url" : url,
        "mode" : mode,
        "ai-result" : aires
        })
    #if not possible then
    #Exception = any error, store it in e and print it
    except Exception as e:
        print(e)
        time.sleep(1)
    json.dump(data_list,file)