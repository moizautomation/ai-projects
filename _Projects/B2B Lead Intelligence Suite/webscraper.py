#Web scraper project (Day 14)
# Goals:
# Extract structured data
# What it should do
# Scrape product/business data
# Store in CSV
# Handle multiple pages
#send description to ai to get summary
import csv
import requests
from bs4 import BeautifulSoup
with open("data.csv","w",newline="") as f:
    #Create a tool that knows how to write rows into CSV
    writer = csv.writer(f)
    #write the heading
    writer.writerow(["Quote", "Author"])
    for page in range(1,5):
        print("\nPage",page)
        url = "https://quotes.toscrape.com/page/" + str(page)
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"html.parser")
        info = soup.find_all("div",class_="quote")
        for quote in info:
            text = quote.find("span",class_="text").text
            author = quote.find("small",class_="author").text
            print(f"Quote: {text}\nAuthor: {author}")
            #now we need to save them into csv in format
            #"quote","author"
            writer.writerow([text,author])
    


