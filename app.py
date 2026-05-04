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

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #f5f7fa; }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1.2rem;
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        color: white;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 0.4rem;
        line-height: 1.2;
    }

    .hero-title span {
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .stats-row {
        display: flex;
        justify-content: center;
        gap: 1.2rem;
        margin: 1.2rem 0;
        flex-wrap: wrap;
    }

    .stat-pill {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 50px;
        padding: 0.35rem 1rem;
        color: #475569;
        font-size: 0.82rem;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .stat-pill b { color: #6366f1; }

    .search-tag {
        display: inline-block;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #3b82f6;
        border-radius: 8px;
        padding: 0.25rem 0.7rem;
        font-size: 0.82rem;
        margin-bottom: 0.5rem;
    }

    [data-testid="stChatMessageContent"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        color: #1e293b !important;
        padding: 1rem 1.2rem !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li { color: #334155 !important; }

    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] b { color: #6366f1 !important; }

    .stChatInputContainer {
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }

    .stChatInputContainer textarea { color: #1e293b !important; font-size: 0.95rem !important; }
    .stChatInputContainer textarea::placeholder { color: #94a3b8 !important; }

    .sidebar-title {
        color: #1e293b;
        font-weight: 600;
        font-size: 0.88rem;
        margin-bottom: 0.6rem;
        letter-spacing: 0.3px;
    }

    .divider { border: none; border-top: 1px solid #f1f5f9; margin: 1rem 0; }

    .tag-chip {
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: #475569;
        border-radius: 50px;
        padding: 0.2rem 0.65rem;
        font-size: 0.78rem;
        margin: 0.2rem 0.15rem 0.2rem 0;
    }

    h1, h2, h3 { color: #1e293b !important; }
    .stMarkdown p { color: #475569 !important; }

    .stButton > button {
        background: #f8fafc !important;
        color: #334155 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.15s !important;
    }

    .stButton > button:hover {
        background: #eff6ff !important;
        border-color: #bfdbfe !important;
        color: #3b82f6 !important;
    }

    #clear-btn button {
        background: #fff1f2 !important;
        border-color: #fecdd3 !important;
        color: #e11d48 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── LLM + Search ──────────────────────────────────────────────────────────────
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
search = DuckDuckGoSearchRun()

system = SystemMessage(content="""
You are a friendly AI Job Agent assistant.

You have two modes:
1. CHAT mode: For greetings, questions, or general conversation — respond naturally and helpfully.
   Example: if someone says "hello", greet them back and offer to help find jobs.
2. SEARCH mode: When the user mentions a job title, role, or skill keywords — search for real UK job listings and present them clearly with job title, company, location, and description using markdown.

Always be friendly and conversational. Never say you can't help.
""")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">💼 AI Job Agent</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;font-size:0.78rem;margin-top:-0.3rem;">Powered by Groq · LLaMA 3</p>', unsafe_allow_html=True)
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

    with st.container():
        st.markdown('<div id="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p style="color:#cbd5e1;font-size:0.72rem;text-align:center;margin-top:1rem;">Searches Indeed UK & Reed UK</p>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">AI-Powered · Live Job Search</div>
    <div class="hero-title">Find Your Next <span>Dream Job</span></div>
    <div class="hero-subtitle">Chat naturally or type job keywords — I'll find live UK listings for you</div>
    <div class="stats-row">
        <div class="stat-pill">🇬🇧 <b>Indeed UK</b> & Reed UK</div>
        <div class="stat-pill">⚡ <b>Real-time</b> results</div>
        <div class="stat-pill">🤖 <b>AI</b> summarised</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat state ────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.session_state.pop("quick_prompt", None)
chat_input = st.chat_input("Say hello or type a job role, e.g. Python developer London...")
if chat_input:
    prompt = chat_input

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # Let LLM decide if this needs a job search
        intent_check = llm.invoke([
            SystemMessage(content="Reply with only 'SEARCH' if the message is asking about jobs, roles, or careers. Reply with 'CHAT' for everything else."),
            HumanMessage(content=prompt)
        ])
        intent = intent_check.content.strip().upper()

        if "SEARCH" in intent:
            st.markdown(f'<div class="search-tag">🔍 Searching: {prompt}</div>', unsafe_allow_html=True)
            with st.spinner("Finding live job listings..."):
                search_result = search.run(f"{prompt} jobs site:indeed.co.uk OR site:reed.co.uk")
                messages = [
                    system,
                    HumanMessage(content=f"User is looking for: {prompt}"),
                    HumanMessage(content=f"Search results:\n{search_result}\n\nSummarise the best matching listings.")
                ]
        else:
            messages = [system, HumanMessage(content=prompt)]

        response = llm.invoke(messages)
        st.markdown(response.content)
        st.session_state.messages.append({"role": "assistant", "content": response.content})
