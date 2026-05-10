#AI Writing Assistant Tool
# User picks a task: write a product description, email, social post, or blog intro
# User fills in simple inputs (topic, tone, length)
# AI generates the content on click
# User can copy or download the result

import google.generativeai as genai
from dotenv import load_dotenv 
import os
import streamlit as st

if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    You are a strict writing AI Assistant.
    You will recieve the task of writing something. eg: description,social post.
    You will also recieve the topic, text and length. Also the tone.
    You will strictly follow all of these things like especially the length and tone should
    be the same user asked for as well as the task you recieved.
    You are going to follow all the below rules striclty.
    Rules:
    - Never give extra text.
    - Stricly follow all the instructions given
    - If you have no information on topic, simply return no result found.
    """)



page = st.sidebar.selectbox("Navigation",["HomePage","Writing Assistant","Instructions"])
if(page == "HomePage"):
    st.title("Home Page")
    st.header("Welcome To AI Writing Assistant")
    
    st.divider()
    st.write("This is the homepage of the Writing Assistant.\nYou can use this tool to write description,emails etc.\nYou can also select the tone, word count and topic.")

if(page == "Writing Assistant"):
    st.title("AI Writing Assistant")
    st.divider()

    if st.session_state.usage_count >= 3:
        st.warning("🔒 **Demo limit reached.**")
        st.info("To get full access or a custom version for your business, contact me:")
        st.markdown("📩 **Email:** abdull.devv@gmail.com")
        st.stop()


    st.header("Input")
    st.divider()
    task = st.selectbox("Task Selector",["Description","Email","Social Post","Blog Intro"])

    topic = st.text_input("Enter the topic: ")

    text = st.text_area("Enter your text: ")

    length = st.selectbox("Length",["0-100 Words","150-200 Words","300-400 words"])

    tone = st.selectbox("Tone",["Friendly","Professional","Casual"])

    button = st.button("Enter")


    if "cache" not in st.session_state:
        st.session_state.cache = {}
    # cleaned = text[:200]
    key = topic + task + tone + length + text[:200]

    if(button):
        if len(topic) == 0 or len(text) == 0:
                st.error("Error! All fields are mandatory")
                st.stop()
        
        st.session_state.usage_count += 1

        with st.spinner(f"Writing the {task}"):
            st.header("AI Result")
            st.divider()
            if key in st.session_state.cache:
                response_text = st.session_state.cache[key]
            else:
                prompt = f"""
                Task:
                {task}

                Topic:
                {topic}

                Text:
                {text}

                length:
                {length}

                Tone:
                {tone}
                """
                
                response = model.generate_content(
                        prompt,
                        generation_config={"max_output_tokens": 200})
                response_text = response.text
                st.session_state.cache[key] = response_text

            st.write(response_text)
            st.download_button(      # ✅ add this
                label="Download Result",
                data=response_text,
                file_name="ai_writing_result.txt",
                mime="text/plain"
            )


if(page == "Instructions"):
    st.title("Instructions")
    st.header("How to use the Tool")
    
    st.write("1. Select the Task eg: write Description, email etc")
    st.write("2. Enter the topic")
    st.write("3. Enter your text")
    st.write("4. Choose the word count you want")
    st.write("5. Select the tone")
    st.write("6. You can also download the result")

                






