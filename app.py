import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)
search = DuckDuckGoSearchRun()

system = SystemMessage(content="""
You are a job search assistant.
When the user gives you keywords or a job title, search for real job listings on Indeed UK or Reed UK.
Always use the search tool to find actual current job postings.
Present results clearly with job title, company, location, and a brief description.
""")

st.title("🤖 AI Job Agent")
st.subheader("Type job keywords to find matching jobs!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("e.g. Python developer London, remote data analyst..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Searching for jobs..."):
            st.write(f"🔍 Searching for: **{prompt}**")
            search_result = search.run(f"{prompt} jobs site:indeed.co.uk OR site:reed.co.uk")

            final_messages = [
                system,
                HumanMessage(content=f"User is looking for: {prompt}"),
                HumanMessage(content=f"Search results:\n{search_result}\n\nSummarise the best matching job listings from these results.")
            ]
            response = llm.invoke(final_messages)
            st.write(response.content)
            st.session_state.messages.append({"role": "assistant", "content": response.content})
