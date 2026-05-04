import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os, io, re, datetime
import pdfplumber
import docx

load_dotenv()

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #f8fafc; }
    section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }

    .hero { text-align:center; padding:1.8rem 1rem 0.8rem; }
    .hero-badge { display:inline-block; background:linear-gradient(90deg,#6366f1,#06b6d4); color:white; font-size:0.7rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:0.28rem 0.9rem; border-radius:50px; margin-bottom:0.7rem; }
    .hero-title { font-size:2.1rem; font-weight:700; color:#1e293b; margin:0 0 0.35rem; }
    .hero-title span { background:linear-gradient(90deg,#6366f1,#06b6d4); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .hero-sub { color:#64748b; font-size:0.92rem; margin-bottom:0.8rem; }
    .pills { display:flex; justify-content:center; gap:0.7rem; flex-wrap:wrap; margin-bottom:1rem; }
    .pill { background:#fff; border:1px solid #e2e8f0; border-radius:50px; padding:0.28rem 0.85rem; color:#475569; font-size:0.77rem; font-weight:500; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
    .pill b { color:#6366f1; }

    [data-testid="stChatMessageContent"] {
        background:#ffffff !important; border:1px solid #e2e8f0 !important;
        border-radius:16px !important; color:#1e293b !important;
        padding:1rem 1.2rem !important; font-size:0.94rem !important;
        line-height:1.72 !important; box-shadow:0 1px 4px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li { color:#334155 !important; }
    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] b { color:#6366f1 !important; }
    [data-testid="stChatMessageContent"] code { background:#f1f5f9; color:#7c3aed; padding:0.1rem 0.4rem; border-radius:4px; font-size:0.88rem; }
    [data-testid="stChatMessageContent"] h1,
    [data-testid="stChatMessageContent"] h2,
    [data-testid="stChatMessageContent"] h3 { color:#1e293b !important; margin-top:0.8rem; }
    [data-testid="stChatMessageContent"] blockquote { border-left:3px solid #6366f1; padding-left:0.8rem; color:#64748b !important; margin:0.5rem 0; }

    .stChatInputContainer { background:#fff !important; border:1.5px solid #e2e8f0 !important; border-radius:16px !important; box-shadow:0 2px 8px rgba(0,0,0,0.05) !important; }
    .stChatInputContainer textarea { color:#1e293b !important; font-size:0.94rem !important; }
    .stChatInputContainer textarea::placeholder { color:#94a3b8 !important; }

    .source-tag { display:inline-block; background:#faf5ff; border:1px solid #ddd6fe; color:#7c3aed; border-radius:8px; padding:0.22rem 0.7rem; font-size:0.78rem; margin-bottom:0.5rem; margin-right:0.4rem; }
    .doc-tag { display:inline-block; background:#f0fdf4; border:1px solid #bbf7d0; color:#16a34a; border-radius:8px; padding:0.22rem 0.7rem; font-size:0.78rem; margin-bottom:0.5rem; margin-right:0.4rem; }
    .doc-card { background:linear-gradient(135deg,#f5f3ff,#eff6ff); border:1px solid #ddd6fe; border-radius:10px; padding:0.6rem 0.9rem; margin-bottom:0.4rem; font-size:0.81rem; color:#4c1d95; }

    .chat-item { padding:0.45rem 0.7rem; border-radius:10px; margin-bottom:0.25rem; cursor:pointer; font-size:0.83rem; border:1px solid transparent; color:#334155; background:#f8fafc; display:flex; justify-content:space-between; align-items:center; }
    .chat-item.active { background:#eff6ff; border-color:#bfdbfe; color:#1d4ed8; font-weight:600; }
    .chat-item:hover { background:#f1f5f9; }
    .chat-time { font-size:0.7rem; color:#94a3b8; }

    .sidebar-title { color:#1e293b; font-weight:600; font-size:0.86rem; margin-bottom:0.5rem; }
    .divider { border:none; border-top:1px solid #f1f5f9; margin:0.85rem 0; }

    .stButton > button { background:#f8fafc !important; color:#334155 !important; border:1px solid #e2e8f0 !important; border-radius:10px !important; font-weight:500 !important; font-size:0.82rem !important; width:100% !important; text-align:left !important; padding:0.45rem 0.75rem !important; }
    .stButton > button:hover { background:#f5f3ff !important; border-color:#ddd6fe !important; color:#7c3aed !important; }
    h1,h2,h3 { color:#1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ── File parsing ──────────────────────────────────────────────────────────────
def extract_text(f) -> str:
    name = f.name.lower()
    data = f.read()
    if name.endswith(".pdf"):
        pages = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t:
                    pages.append(t)
        return "\n".join(pages)
    elif name.endswith(".docx"):
        d = docx.Document(io.BytesIO(data))
        return "\n".join([p.text for p in d.paragraphs if p.text.strip()])
    else:
        return data.decode("utf-8", errors="ignore")

# ── Live query detection ──────────────────────────────────────────────────────
LIVE_KEYWORDS = re.compile(
    r"\b(score|scores|ipl|cricket|football|match|live|weather|temperature|forecast|"
    r"today|tonight|right now|currently|latest|news|stock|price|rate|exchange|"
    r"trending|update|breaking|happened|win|won|lost|playing|result|standings|"
    r"premier league|nba|nfl|f1|grand prix|election|covid|inflation|rainfall|humidity)\b",
    re.IGNORECASE
)

def is_live_query(text: str) -> bool:
    return bool(LIVE_KEYWORDS.search(text))

# ── LLM + Search ──────────────────────────────────────────────────────────────
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
search = DuckDuckGoSearchRun()

SYSTEM = SystemMessage(content="""You are a smart, fast, friendly AI assistant.
- Answer clearly using markdown (bold key info, bullet points, headers where needed).
- For live data (scores, weather, news): highlight the key facts at the very top.
- For documents: answer based only on the provided document content.
- Keep responses focused, accurate, and well-structured.""")

# ── Session defaults ──────────────────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"
if "docs" not in st.session_state:
    st.session_state.docs = {}

def current_messages():
    return st.session_state.chats[st.session_state.active_chat]

def new_chat():
    n = len(st.session_state.chats) + 1
    name = f"Chat {n}"
    while name in st.session_state.chats:
        n += 1
        name = f"Chat {n}"
    st.session_state.chats[name] = []
    st.session_state.active_chat = name

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;font-size:0.75rem;margin-top:-0.3rem;">Powered by Groq · LLaMA 3.1</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # New chat button
    if st.button("✏️  New Chat"):
        new_chat()
        st.rerun()

    # Chat list
    st.markdown('<div class="sidebar-title" style="margin-top:0.6rem;">💬 Chats</div>', unsafe_allow_html=True)
    for chat_name in list(st.session_state.chats.keys()):
        is_active = chat_name == st.session_state.active_chat
        msg_count = len(st.session_state.chats[chat_name])
        col1, col2 = st.columns([0.78, 0.22])
        with col1:
            label = f"{'● ' if is_active else ''}{chat_name}  ({msg_count})"
            if st.button(label, key=f"chat_{chat_name}"):
                st.session_state.active_chat = chat_name
                st.rerun()
        with col2:
            if len(st.session_state.chats) > 1:
                if st.button("✕", key=f"del_chat_{chat_name}"):
                    del st.session_state.chats[chat_name]
                    st.session_state.active_chat = list(st.session_state.chats.keys())[0]
                    st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Document upload
    st.markdown('<div class="sidebar-title">📎 Documents</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("PDF, DOCX, TXT", type=["pdf","docx","txt"], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded:
        for f in uploaded:
            if f.name not in st.session_state.docs:
                with st.spinner(f"Reading {f.name}..."):
                    st.session_state.docs[f.name] = extract_text(f)
    for fname in list(st.session_state.docs.keys()):
        c1, c2 = st.columns([0.82, 0.18])
        with c1:
            st.markdown(f'<div class="doc-card">📄 <b>{fname}</b></div>', unsafe_allow_html=True)
        with c2:
            if st.button("✕", key=f"ddel_{fname}"):
                del st.session_state.docs[fname]
                st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="sidebar-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
    for label, prompt_text in [
        ("🏏 IPL live score", "What is the live IPL score today?"),
        ("🌦️ Weather in London", "What is the current weather in London?"),
        ("📰 Latest tech news", "What are the latest technology news headlines today?"),
        ("📄 Summarise document", "Please summarise all the uploaded documents"),
        ("❓ Quiz from document", "Create a 5-question quiz from my uploaded documents"),
        ("📝 Key points from doc", "What are the key points from my uploaded documents?"),
    ]:
        if st.button(label, key=f"qa_{label}"):
            st.session_state["quick_prompt"] = prompt_text

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️  Clear This Chat"):
        st.session_state.chats[st.session_state.active_chat] = []
        st.rerun()

# ── Hero ──────────────────────────────────────────────────────────────────────
doc_count = len(st.session_state.docs)
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">Live Search · Documents · Multi-Chat</div>
    <div class="hero-title">Your <span>AI Assistant</span></div>
    <div class="hero-sub">Ask anything — live scores, weather, news, or questions about your documents</div>
    <div class="pills">
        <div class="pill">🌐 <b>Live</b> web search</div>
        <div class="pill">📄 <b>Document</b> Q&A</div>
        <div class="pill">🏏 <b>Sports</b> scores</div>
        <div class="pill">🌦️ <b>Weather</b></div>
        {"<div class='pill'>📎 <b>" + str(doc_count) + "</b> doc(s)</div>" if doc_count else ""}
        <div class="pill">💬 <b>{len(st.session_state.chats)}</b> chat(s)</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"#### {st.session_state.active_chat}")

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in current_messages():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.session_state.pop("quick_prompt", None)
user_input = st.chat_input("Ask anything — IPL score, weather, summarise my doc, explain a topic...")
if user_input:
    prompt = user_input

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    current_messages().append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        use_web = is_live_query(prompt)
        has_docs = bool(st.session_state.docs)
        doc_query = any(w in prompt.lower() for w in ["document","doc","uploaded","file","summarise","summary","quiz","notes","pdf","text"])

        messages = [SYSTEM]
        for m in current_messages()[:-1][-6:]:
            cls = HumanMessage if m["role"] == "user" else SystemMessage
            messages.append(cls(content=m["content"]))

        tags_html = ""

        if use_web:
            tags_html += '<span class="source-tag">🌐 Live search</span>'
            with st.spinner("Searching the web..."):
                web_data = search.run(prompt)
            messages.append(HumanMessage(content=f"Question: {prompt}\n\nLive web results:\n{web_data}\n\nAnswer using these results. Put key facts first."))

        elif has_docs and (doc_query or not use_web):
            tags_html += '<span class="doc-tag">📄 Using your documents</span>'
            combined = "\n\n---\n\n".join([f"[{n}]\n{t[:4000]}" for n, t in st.session_state.docs.items()])
            messages.append(HumanMessage(content=f"Documents:\n{combined}\n\nQuestion: {prompt}"))

        else:
            messages.append(HumanMessage(content=prompt))

        if tags_html:
            st.markdown(tags_html, unsafe_allow_html=True)

        with st.spinner("Thinking..."):
            response = llm.invoke(messages)

        st.markdown(response.content)
        current_messages().append({"role": "assistant", "content": response.content})
