#Lead Generation Bot Project
# Goals:
# Extract structured data
# What it should do
# Scrape product/business data
# Store in JSON
# Handle multiple pages
#send description to ai to get summary

import sqlite3
import google.generativeai as genai
import time
import json
from dotenv import load_dotenv 
import os
import csv
import requests
from bs4 import BeautifulSoup


load_dotenv()

conn = sqlite3.connect("Product.db")
cursor = conn.cursor()

# cursor.execute("""CREATE TABLE IF NOT EXISTS products(
#                id INTEGER PRIMARY KEY AUTOINCREMENT,
#                name TEXT,
#                price FLOAT,
#                description TEXT,
#                ratings FLOAT,
#                link TEXT,
#                summary TEXT,
#                unique_key TEXT UNIQUE)""")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    You must act like a strict assistant. 
    You will only return short useful information for the given context.
    Format:
    Ai Summary: [Short summary of the description in 3-4 simple words]
    Rules:
    -No extra text
    -Strictly Follow the above format
    """)

#empty set to store the data of each product
#used for duplication check
data_list = []


    
#make scraper look like a real browser instead of bot
headers = {
"User-Agent": "Mozilla/5.0"
}
url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops" 
r = requests.get(url, headers = headers)

#error handling
if r.status_code != 200:
    print("Failed to fetch page:", r.status_code)
    exit()

#getting the html thorough beautiful soup
soup = BeautifulSoup(r.text,"html.parser")
#finding the main divs containing all product data
info = soup.find_all("div",class_="card thumbnail")


#going through each div through loop
for product in info:
    ai_summary = "API Failed"
    #finding the name
    name = product.find("a",class_="title").text
    #stripping garbage values like \n from name
    name = name.strip()

    #extracting price
    price = product.find("span",attrs={"itemprop" : "price"}).text
    
    #extracting description
    desc = product.find("p",class_="description card-text").text
    #stripping garbage values like \n from description
    desc = desc.strip()

    #finding ratings
    rating = product.find("p",attrs={"data-rating" : True})
    ratings = rating.attrs["data-rating"] + " " + "stars" if rating else "N/A"

    link = product.find("a",attrs={"href" : True})
    #making the link safe
    href = link.attrs["href"] if link else "#"
    #making the complete link of that product
    full_link = "https://webscraper.io" + href

    #Making the unique key to identify each product
    key = name + " " + price + " " + href

    try:
        response = model.generate_content(desc)
        ai_summary = response.text.strip()
    #if not possible then
    #Exception = any error, store it in e and print it
    except Exception as e:
        print(e)
        time.sleep(60)

    # if(price != "" and len(name) != 0 and key not in keys):, its cleaner version is below
    cursor.execute("""INSERT OR IGNORE INTO products(name,price,description,ratings,link,summary,unique_key) 
                   VALUES(:name,:price,:description,:ratings,:link,:summary,:unique_key)""",{"name" : name,"price" : price,"description" : desc,"ratings" : ratings,"link" : full_link,"summary" : ai_summary,"unique_key" : key})
conn.commit()
cursor.execute("CREATE INDEX product_id_idx ON products(name)")

cursor.execute("SELECT * FROM products")
data = cursor.fetchall()

print(f"data: {data}")

conn.close()



