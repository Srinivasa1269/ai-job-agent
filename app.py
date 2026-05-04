import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Study AI", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #f8fafc; }
    section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }

    .hero { text-align:center; padding: 2rem 1rem 1rem; }
    .hero-badge { display:inline-block; background:linear-gradient(90deg,#8b5cf6,#3b82f6); color:white; font-size:0.72rem; font-weight:600; letter-spacing:2px; text-transform:uppercase; padding:0.3rem 1rem; border-radius:50px; margin-bottom:0.8rem; }
    .hero-title { font-size:2.3rem; font-weight:700; color:#1e293b; margin:0 0 0.4rem; }
    .hero-title span { background:linear-gradient(90deg,#8b5cf6,#3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .hero-sub { color:#64748b; font-size:0.97rem; }

    .stats-row { display:flex; justify-content:center; gap:1rem; margin:1rem 0; flex-wrap:wrap; }
    .stat-pill { background:#fff; border:1px solid #e2e8f0; border-radius:50px; padding:0.3rem 0.9rem; color:#475569; font-size:0.8rem; font-weight:500; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
    .stat-pill b { color:#8b5cf6; }

    [data-testid="stChatMessageContent"] {
        background:#ffffff !important; border:1px solid #e2e8f0 !important;
        border-radius:16px !important; color:#1e293b !important;
        padding:1rem 1.2rem !important; font-size:0.95rem !important;
        line-height:1.7 !important; box-shadow:0 1px 4px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li { color:#334155 !important; }
    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] b { color:#8b5cf6 !important; }
    [data-testid="stChatMessageContent"] h1,
    [data-testid="stChatMessageContent"] h2,
    [data-testid="stChatMessageContent"] h3 { color:#1e293b !important; }
    [data-testid="stChatMessageContent"] code { background:#f1f5f9; color:#7c3aed; padding:0.1rem 0.4rem; border-radius:4px; }
    [data-testid="stChatMessageContent"] blockquote { border-left:3px solid #8b5cf6; padding-left:0.8rem; color:#64748b !important; }

    .stChatInputContainer { background:#fff !important; border:1.5px solid #e2e8f0 !important; border-radius:16px !important; box-shadow:0 2px 8px rgba(0,0,0,0.05) !important; }
    .stChatInputContainer textarea { color:#1e293b !important; font-size:0.95rem !important; }
    .stChatInputContainer textarea::placeholder { color:#94a3b8 !important; }

    .web-tag { display:inline-block; background:#faf5ff; border:1px solid #ddd6fe; color:#7c3aed; border-radius:8px; padding:0.22rem 0.7rem; font-size:0.8rem; margin-bottom:0.5rem; }

    .sidebar-title { color:#1e293b; font-weight:600; font-size:0.88rem; margin-bottom:0.5rem; }
    .divider { border:none; border-top:1px solid #f1f5f9; margin:0.9rem 0; }
    .topic-chip { display:inline-block; background:#f5f3ff; border:1px solid #ddd6fe; color:#6d28d9; border-radius:50px; padding:0.2rem 0.65rem; font-size:0.78rem; margin:0.15rem; }

    .stButton > button { background:#f8fafc !important; color:#334155 !important; border:1px solid #e2e8f0 !important; border-radius:10px !important; font-weight:500 !important; font-size:0.83rem !important; width:100% !important; text-align:left !important; }
    .stButton > button:hover { background:#f5f3ff !important; border-color:#ddd6fe !important; color:#7c3aed !important; }
    h1,h2,h3 { color:#1e293b !important; }
    .stMarkdown p { color:#475569 !important; }
</style>
""", unsafe_allow_html=True)

# ── LLM + Search ──────────────────────────────────────────────────────────────
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
search = DuckDuckGoSearchRun()

SYSTEM = SystemMessage(content="""
You are a smart, friendly study assistant.

Rules:
- Explain concepts clearly with examples, analogies, and structure.
- Use markdown: headers, bullet points, bold key terms, code blocks where relevant.
- If asked to quiz the user, give MCQ or short-answer questions with answers at the end.
- If asked to summarise, be concise but complete.
- If web search results are provided, use them to give accurate, up-to-date answers and cite the source topic.
- Always be encouraging and supportive.
""")

def needs_web_search(prompt: str) -> bool:
    check = llm.invoke([
        SystemMessage(content="Reply ONLY 'YES' if the question needs live/current/recent information from the web (news, current events, latest research, real-time data). Reply 'NO' if it can be answered from general knowledge."),
        HumanMessage(content=prompt)
    ])
    return "YES" in check.content.strip().upper()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">📚 Study AI</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;font-size:0.78rem;margin-top:-0.3rem;">Your AI study companion</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
    quick = {
        "📝 Quiz me on this topic": "Quiz me with 5 questions on the last topic we discussed",
        "📖 Summarise what we covered": "Summarise everything we have discussed so far in bullet points",
        "🔍 Explain in simple terms": "Explain the last concept in the simplest way possible, like I'm 10",
        "📊 Give me key formulas": "List all key formulas or facts related to what we discussed",
        "🌐 Search latest info": "Search the web for the latest information on the last topic",
    }
    for label, prompt_text in quick.items():
        if st.button(label, key=f"q_{label}"):
            st.session_state["quick_prompt"] = prompt_text

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📂 Study Topics</div>', unsafe_allow_html=True)
    subjects = ["Mathematics","Physics","Chemistry","Biology","History","Computer Science","Economics","Literature","Psychology","Law"]
    st.markdown(" ".join([f'<span class="topic-chip">{s}</span>' for s in subjects]), unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
    always_search = st.toggle("Always search the web", value=False)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">AI Study Assistant · Live Web Search</div>
    <div class="hero-title">Your Personal <span>Study AI</span></div>
    <div class="hero-sub">Ask anything — concepts, quizzes, summaries, or live research from the web</div>
    <div class="stats-row">
        <div class="stat-pill">🧠 <b>Explain</b> any topic</div>
        <div class="stat-pill">📝 <b>Quiz</b> yourself</div>
        <div class="stat-pill">🌐 <b>Live</b> web search</div>
        <div class="stat-pill">📖 <b>Summarise</b> notes</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat state ────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.session_state.pop("quick_prompt", None)
user_input = st.chat_input("Ask anything — e.g. Explain photosynthesis, Quiz me on WW2, Latest AI research...")
if user_input:
    prompt = user_input

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        use_web = always_search or needs_web_search(prompt)

        messages = [SYSTEM]
        for m in st.session_state.messages[:-1][-6:]:  # last 6 messages as context
            role = HumanMessage if m["role"] == "user" else SystemMessage
            messages.append(role(content=m["content"]))

        if use_web:
            st.markdown('<div class="web-tag">🌐 Searching the web...</div>', unsafe_allow_html=True)
            with st.spinner("Fetching live information..."):
                web_results = search.run(prompt)
                messages.append(HumanMessage(content=f"Question: {prompt}\n\nLive web results:\n{web_results}\n\nAnswer using these results, cite sources where relevant."))
        else:
            messages.append(HumanMessage(content=prompt))

        with st.spinner("Thinking..."):
            response = llm.invoke(messages)

        st.markdown(response.content)
        st.session_state.messages.append({"role": "assistant", "content": response.content})
