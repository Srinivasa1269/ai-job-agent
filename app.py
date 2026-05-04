import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="AI Job Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(90deg, #6c63ff, #3ecfcf);
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        margin: 0 0 0.5rem;
        line-height: 1.2;
    }

    .hero-title span {
        background: linear-gradient(90deg, #6c63ff, #3ecfcf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.55);
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }

    .stats-row {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1.5rem 0;
    }

    .stat-pill {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 50px;
        padding: 0.4rem 1.1rem;
        color: rgba(255,255,255,0.75);
        font-size: 0.82rem;
        font-weight: 500;
    }

    .stat-pill b {
        color: #3ecfcf;
    }

    .chat-area {
        max-width: 820px;
        margin: 0 auto;
        padding: 0 1rem;
    }

    .stChatMessage {
        background: transparent !important;
    }

    [data-testid="stChatMessageContent"] {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 16px !important;
        color: rgba(255,255,255,0.9) !important;
        padding: 1rem 1.2rem !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
    }

    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li,
    [data-testid="stChatMessageContent"] span {
        color: rgba(255,255,255,0.88) !important;
    }

    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] b {
        color: #3ecfcf !important;
    }

    .search-tag {
        display: inline-block;
        background: rgba(108,99,255,0.2);
        border: 1px solid rgba(108,99,255,0.4);
        color: #a89cff;
        border-radius: 8px;
        padding: 0.25rem 0.7rem;
        font-size: 0.82rem;
        margin-bottom: 0.6rem;
    }

    .stChatInputContainer {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stChatInputContainer textarea {
        color: white !important;
        font-size: 0.95rem !important;
    }

    .stChatInputContainer textarea::placeholder {
        color: rgba(255,255,255,0.35) !important;
    }

    .stSpinner > div {
        border-top-color: #6c63ff !important;
    }

    .sidebar-section {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .sidebar-title {
        color: rgba(255,255,255,0.9);
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.6rem;
        letter-spacing: 0.5px;
    }

    .tag-chip {
        display: inline-block;
        background: rgba(108,99,255,0.18);
        border: 1px solid rgba(108,99,255,0.35);
        color: #b0aaff;
        border-radius: 50px;
        padding: 0.2rem 0.65rem;
        font-size: 0.78rem;
        margin: 0.2rem 0.2rem 0.2rem 0;
        cursor: pointer;
    }

    .divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 1.2rem 0;
    }

    h1, h2, h3 { color: white !important; }

    .stMarkdown p { color: rgba(255,255,255,0.75) !important; }

    .stButton > button {
        background: linear-gradient(90deg, #6c63ff, #3ecfcf) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">💼 AI Job Agent</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:rgba(255,255,255,0.45);font-size:0.8rem;margin-top:-0.4rem;">Powered by Groq · LLaMA 3</p>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">⚡ Quick Searches</div>', unsafe_allow_html=True)
    quick_searches = [
        "Python Developer London",
        "Remote Data Analyst",
        "Frontend React Engineer",
        "Machine Learning Engineer",
        "DevOps AWS Remote",
        "Product Manager Tech",
    ]
    for qs in quick_searches:
        if st.button(qs, key=f"qs_{qs}"):
            st.session_state["quick_prompt"] = qs

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">🔥 Popular Skills</div>', unsafe_allow_html=True)
    skills = ["Python", "React", "AWS", "SQL", "Docker", "Node.js", "Kubernetes", "TypeScript"]
    st.markdown(" ".join([f'<span class="tag-chip">{s}</span>' for s in skills]), unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<p style="color:rgba(255,255,255,0.25);font-size:0.72rem;text-align:center;margin-top:1rem;">Searches Indeed UK & Reed UK</p>', unsafe_allow_html=True)

# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">AI-Powered · Live Job Search</div>
    <div class="hero-title">Find Your Next <span>Dream Job</span></div>
    <div class="hero-subtitle">Type any role or keyword — get live results from the UK's top job boards</div>
    <div class="stats-row">
        <div class="stat-pill">🇬🇧 <b>Indeed UK</b> & Reed UK</div>
        <div class="stat-pill">⚡ <b>Real-time</b> results</div>
        <div class="stat-pill">🤖 <b>AI</b> summarised</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LLM + Search setup ────────────────────────────────────────────────────────
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
search = DuckDuckGoSearchRun()

system = SystemMessage(content="""
You are a job search assistant.
When the user gives you keywords or a job title, search for real job listings on Indeed UK or Reed UK.
Present results clearly with job title, company, location, and a brief description.
Use markdown formatting with bold job titles and bullet points.
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle quick search sidebar buttons
if "quick_prompt" in st.session_state:
    prompt = st.session_state.pop("quick_prompt")
else:
    prompt = None

chat_input = st.chat_input("e.g. Python developer London, remote data analyst...")
if chat_input:
    prompt = chat_input

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        st.markdown(f'<div class="search-tag">🔍 Searching: {prompt}</div>', unsafe_allow_html=True)
        with st.spinner("Finding live job listings..."):
            search_result = search.run(f"{prompt} jobs site:indeed.co.uk OR site:reed.co.uk")

            final_messages = [
                system,
                HumanMessage(content=f"User is looking for: {prompt}"),
                HumanMessage(content=f"Search results:\n{search_result}\n\nSummarise the best matching job listings from these results.")
            ]
            response = llm.invoke(final_messages)
            st.markdown(response.content)
            st.session_state.messages.append({"role": "assistant", "content": response.content})
