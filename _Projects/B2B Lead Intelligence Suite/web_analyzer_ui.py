#Lead Generation Bot Project
# Goals:
# Extract structured data
# What it should do
# Scrape product/business data
# Store in JSON
# Handle multiple pages
#send description to ai to get summary

import google.generativeai as genai
import json
from dotenv import load_dotenv 
import os
import requests
from bs4 import BeautifulSoup
import streamlit as st

if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

load_dotenv()

# This looks for the key in your local .env OR in Streamlit's Secret settings
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

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
    "keypoints": ["Key point 1","Key Point 2", "Key Point 3"]
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

page = st.sidebar.selectbox("Navigate", ["Home", "Tool","Instructions"])
if page == "Home":
    st.title("Home Page")
    st.text("This AI tool is used to scrape data from any website\n and give you its Summary, Key Points, or the Sentiment of the Website.")
    st.write("This is the homepage content")

elif page == "Tool":
    st.title("AI Tool")

    if st.session_state.usage_count >= 3:
        st.warning("🔒 **Demo limit reached.**")
        st.info("To unlock unlimited analysis or request a custom build for your agency, contact me:")
        st.markdown("📩 **Email:** abdull.devv@gmail.com")
        st.stop()

    st.header("Web AI Analyzer")
    st.divider()

    st.subheader("Input")
    st.divider()

    url = st.text_area("Enter the Target URL: ")
    uploaded_file = st.file_uploader("Upload your File: ",type=["txt"])

    mode = st.selectbox("Choose mode",["Summary","Key Points","Sentiment"])
    button = st.button("Enter")

    st.subheader("Output")
    st.divider()


    if button:
        #Input Validation
        if(len(url) != 0 and uploaded_file is not None):
            st.error("Error! Cannot use both URL and File Upload at the same time")
            st.stop()

        if(len(url) == 0 and uploaded_file is None):
            st.error("Error! Both cannot be empty")
            st.stop()

        st.session_state.usage_count += 1

        cleaned = ""
        key = ""

        with st.spinner("Processing...."):
            if(len(url) > 0):
                url = url.strip()
                key = url + mode
                if not url.startswith("http"):
                    st.error("Invalid URL")
                    st.stop()
                try:
                    r = requests.get(url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")

                    data = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])

                    for el in data:
                        cleaned += el.text.strip() + "\n"
                except:
                    st.error("Website cannot be reached")
                    st.stop()
            elif uploaded_file is not None:
                    cleaned = uploaded_file.read().decode("utf-8").strip()

                    key = cleaned[:100] + mode

            if "cache" not in st.session_state:
                st.session_state.cache = {}
            
            if key in st.session_state.cache:
                response_text = st.session_state.cache[key]
            else:
                prompt = f"""
                Text:
                {cleaned}

                Mode:
                {mode}

                IMPORTANT:
                Return ONLY valid JSON.
                """

                response = model.generate_content(
                    prompt,
                    generation_config={"max_output_tokens": 200}
                )

                # try:
                    #used to convert string into json by reading through it
                    # json_data = json.loads(response_text)

                    #Output
            st.subheader("AI Result")
            response_text = response.text
            st.session_state.cache[key] = response_text
            st.write(response_text)
            st.download_button(
                label = "Download Results",
                data = response_text,
                file_name = "ai_result.json",
                mime="application/json"
            )
                # except:
                #     st.subheader("AI Result")
                #     st.error("Error! Ai return invalid result")

elif page == "Instructions":
    st.title("Instructions")
    st.write("How to use the Tool")
    st.write("1. Input you URL or upload File")
    st.write("2. Choose one of the modes")
    st.write("3. Press Enter")
    st.write("4. Result will be shown below")
    st.write("5. You can download it using the download button")

   



