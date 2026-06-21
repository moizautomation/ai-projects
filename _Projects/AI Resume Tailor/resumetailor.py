# user upload the resume with and paste the job description
# ai tailors resume according to the description
# give a matching score with the job
# give the tailored resume to the user for download.

from pypdf import PdfReader
import streamlit as st
import google.generativeai as genai
import json
from dotenv import load_dotenv 
import os

load_dotenv()

# This looks for the key in your local .env OR in Streamlit's Secret settings
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    You are a job description analyst. Your only job is to extract structured information from job descriptions.

STRICT RULES:
1. Never guess or assume. Only extract what is explicitly stated in the job description.
2. Always return valid JSON. Nothing before it. Nothing after it. No markdown. No backticks.
3. Always follow this exact structure:

{
  "skills": [
    "list of programming languages, frameworks, tools, databases, and technical skills mentioned"
  ],
  "responsibilities": [
    "list of actual job responsibilities and duties mentioned"
  ],
  "keywords": [
    "list of important domain keywords and concepts mentioned"
  ]
}

4. Skills must only include technical skills explicitly mentioned. No soft skills.
5. Responsibilities must be concise action phrases starting with a verb.
6. Keywords must be domain-level concepts not specific tools.
7. If a category has nothing to extract return an empty list for that category.
8. Never add skills, responsibilities, or keywords that are not in the job description.
9. Never combine two items into one. Each item in the list must be a single distinct thing.
10. Return only JSON. No explanation. No preamble. No closing remarks.
"""
)

st.title("📄 AI Resume Tailor")

st.divider()

st.header("Input")
st.divider()

resume = st.file_uploader("Upload Resume",type=["pdf"])

job_description = st.text_area("Job Description")
st.divider()

button = st.button("Tailor Resume")

if button:
    if resume is None:
        st.error("Please Upload your Resume")
        st.stop()

    if len(job_description) == 0:
        st.error("Job Description cannot be empty")
        st.stop()    

    with st.spinner("Tailoring your resume"):
        reader = PdfReader(resume)


        if len(reader.pages) == 0:
            st.error("PDF cannot be Empty")
            st.stop()

        text = ""

        for page in reader.pages:

            if page.extract_text() is not None:
                text += page.extract_text()

        text = text.strip()
        
        st.divider()

        # st.write(text)

        prompt = f"""
        The job description is given below:
        {job_description}
"""
        response = model.generate_content(prompt)

        st.header("Output")
        st.divider()

        response_json = json.loads(response.text)

        st.write(response_json)






