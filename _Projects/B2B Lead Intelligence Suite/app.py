# AI lead Intelligence Tool
# User pastes a list of company names or URLs
# Tool scrapes each company's website automatically
# AI analyzes each one: what they do, who they target, pain points
# Output: a clean report per company — ready to use for outreach
# Streamlit UI with download button for the full report

import google.generativeai as genai
import json
from dotenv import load_dotenv 
import os
import requests
from bs4 import BeautifulSoup
import streamlit as st

if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

header = {
    "User-Agent": "Mozilla/5.0"
}

load_dotenv()

# This looks for the key in your local .env OR in Streamlit's Secret settings
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""You are a business intelligence assistant.
if there is very less or no content just return No Useful content.
Analyze the company data below and respond strictly in JSON:

{
 "what_the_company_does": "",
  "target_audience": "",
  "main_product_or_service": "",
  "customer_pain_points": "",
  "sales_or_marketing_angle": ""
}
Rules:
- Be concise
- No extra text
- Return ONLY a valid JSON object
- Use exactly these keys
- Do not add extra fields
- Do not include explanation or text outside JSON
- no ```json
- no backticks"""
)

choice = st.sidebar.selectbox("Navigation",["HomePage","AI Lead Intelligence Tool","Instructions"])
visited_url = []

if(choice == "HomePage"):
    st.title("HomePage")
    st.header("AI Lead Intelligence Tool")
    st.divider()

    st.write("This is a Lead Intelligence AI Tool")
    st.write("You just need to paste the list of URL")
    st.write("It will tell you all the data about each url")

elif(choice == "AI Lead Intelligence Tool"):
    url_data = []
    #to store data of multiple comapnies
    all_reports = []

    st.title("AI Lead Intelligence Tool")
    if st.session_state.usage_count >= 3:
        st.warning("🔒 **Demo limit reached.**")
        st.info("I hope you enjoyed the tool! To get full access for your business or to see more of my work, contact me:")
        st.markdown("📩 **Email:** abdull.devv@gmail.com")
        st.stop()

    st.header("Input")
    st.divider()

    urls = st.text_area("Paste the Companies URL Below:")

    button = st.button("Analyze Companies")

    st.header("Analyzed Results")
    st.divider()

    if "cache" not in st.session_state:
        st.session_state.cache = {}

    if button:
        if(len(urls) == 0):
            st.error("URL Field cannot be empty")
            st.stop()

        st.session_state.usage_count += 1

        with st.spinner("Analyzing your Competitors"):
            urls = urls.split("\n")

            for url in urls:
                cleaned = ""

                url = url.strip()
                if url in visited_url:
                    continue

                if(len(url) == 0):
                    continue

                visited_url.append(url)
                
                if not url.startswith("http"):
                    url = "https://" + url
                
                try:
                    r = requests.get(url,headers=header,timeout=10)

                    if r.status_code != 200:
                        st.error(f"Website {url} cannot be reached Error: {r.status_code}")
                        continue

                    info = BeautifulSoup(r.text,"html.parser")

                    data = info.find_all(["h1","h2","h3","h4","h5","h6","p"])
                    
                    for el in data:
                        cleaned += el.text.strip() + "\n"
                    
                    if len(cleaned) < 50:
                        st.error(f"Not Enough Content found for: {url}")
                        continue
                    key = url.strip().lower()
                    url_data.append(cleaned)
                    
                    cleaned = cleaned[:5000]
                    if key in st.session_state.cache:
                        response_text = st.session_state.cache[key]
                    else:
                        prompt = f"""
                        Data:
                        {cleaned}
                        """
                        response = model.generate_content(prompt)
                        response_text = response.text
                        st.session_state.cache[key] = response_text
                    
                    #to store data of a single company
                    st.subheader(url)
                    st.write(response_text)
                    report = {}
                    report.update({"URL" : url, "AI Analysis" : response_text})
                    all_reports.append(report)
                except Exception as e:
                    st.error(f"Error for {url}: {e}")
                    continue
            #json dumps convert python text into json
            json_data = json.dumps(all_reports,indent = 4)
            st.download_button(
                label = "Download Results",
                data = json_data,
                file_name = "ai_result.json",
                mime="application/json"
            )

elif(choice == "Instructions"):
    st.title("Instructions")
    st.header("How to use the Tool")
    st.divider()

    st.write("1. User pastes a list of company names or URLs")
    st.write("2. Tool scrapes each company's website automatically")
    st.write("3. AI analyzes each one: what they do, who they target, pain points")
    st.write("4. Output: a clean report per company — ready to use for outreach")
    st.write("5. Streamlit UI with download button for the full report")


