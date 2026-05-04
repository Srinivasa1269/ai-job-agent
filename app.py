import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os, io, re, datetime
import pdfplumber
import docx

load_dotenv()

st.set_page_config(page_title="Study", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Colourful pastel page background */
    .stApp {
        background: linear-gradient(160deg, #fdf4ff 0%, #eff6ff 35%, #f0fdf4 65%, #fff7ed 100%);
        min-height: 100vh;
    }

    /* Sidebar: soft lavender tint */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fdf4ff 0%, #eff6ff 100%);
        border-right: 1px solid #e9d5ff;
    }

    /* Hero */
    .hero { text-align:center; padding:1.8rem 1rem 0.8rem; }
    .hero-badge {
        display:inline-block;
        background: linear-gradient(90deg,#a855f7,#3b82f6,#06b6d4);
        color:white; font-size:0.7rem; font-weight:700; letter-spacing:2px;
        text-transform:uppercase; padding:0.28rem 0.9rem; border-radius:50px; margin-bottom:0.7rem;
    }
    .hero-title { font-size:2.5rem; font-weight:800; color:#1e293b; margin:0 0 0.35rem; }
    .hero-title span {
        background: linear-gradient(90deg,#a855f7,#3b82f6,#10b981);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .hero-sub { color:#6b7280; font-size:0.93rem; margin-bottom:0.8rem; }

    /* Colourful pills — each a different pastel */
    .pills { display:flex; justify-content:center; gap:0.6rem; flex-wrap:wrap; margin-bottom:1rem; }
    .pill-purple  { background:#fdf4ff; border:1.5px solid #e9d5ff; color:#7c3aed; border-radius:50px; padding:0.3rem 0.9rem; font-size:0.77rem; font-weight:600; }
    .pill-blue    { background:#eff6ff; border:1.5px solid #bfdbfe; color:#2563eb; border-radius:50px; padding:0.3rem 0.9rem; font-size:0.77rem; font-weight:600; }
    .pill-green   { background:#f0fdf4; border:1.5px solid #bbf7d0; color:#16a34a; border-radius:50px; padding:0.3rem 0.9rem; font-size:0.77rem; font-weight:600; }
    .pill-orange  { background:#fff7ed; border:1.5px solid #fed7aa; color:#ea580c; border-radius:50px; padding:0.3rem 0.9rem; font-size:0.77rem; font-weight:600; }
    .pill-pink    { background:#fdf2f8; border:1.5px solid #fbcfe8; color:#db2777; border-radius:50px; padding:0.3rem 0.9rem; font-size:0.77rem; font-weight:600; }
    .pill-teal    { background:#f0fdfa; border:1.5px solid #99f6e4; color:#0f766e; border-radius:50px; padding:0.3rem 0.9rem; font-size:0.77rem; font-weight:600; }

    /* Chat bubbles: alternating pastel colours */
    [data-testid="stChatMessageContent"] {
        border-radius:18px !important; color:#1e293b !important;
        padding:1rem 1.2rem !important; font-size:0.94rem !important;
        line-height:1.72 !important;
    }
    /* User bubble: soft purple */
    [data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"],
    div[class*="stChatMessage"]:has(img[alt="user"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg,#fdf4ff,#eff6ff) !important;
        border:1.5px solid #e9d5ff !important;
        box-shadow: 0 2px 8px rgba(168,85,247,0.08) !important;
    }
    /* Assistant bubble: soft mint/blue */
    [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg,#f0fdf4,#eff6ff) !important;
        border:1.5px solid #bbf7d0 !important;
        box-shadow: 0 2px 8px rgba(16,185,129,0.07) !important;
    }
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li { color:#334155 !important; }
    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] b { color:#7c3aed !important; }
    [data-testid="stChatMessageContent"] code { background:#fdf4ff; color:#7c3aed; padding:0.1rem 0.4rem; border-radius:4px; font-size:0.88rem; }
    [data-testid="stChatMessageContent"] h1,
    [data-testid="stChatMessageContent"] h2,
    [data-testid="stChatMessageContent"] h3 { color:#1e293b !important; margin-top:0.8rem; }
    [data-testid="stChatMessageContent"] blockquote { border-left:3px solid #a855f7; padding-left:0.8rem; color:#6b7280 !important; }

    /* Input bar */
    .stChatInputContainer {
        background: linear-gradient(135deg,#fdf4ff,#eff6ff) !important;
        border:1.5px solid #e9d5ff !important; border-radius:18px !important;
        box-shadow: 0 4px 16px rgba(168,85,247,0.1) !important;
    }
    .stChatInputContainer textarea { color:#1e293b !important; font-size:0.94rem !important; background:transparent !important; }
    .stChatInputContainer textarea::placeholder { color:#a78bfa !important; }

    /* Tags */
    .source-tag { display:inline-block; background:#eff6ff; border:1.5px solid #bfdbfe; color:#2563eb; border-radius:8px; padding:0.22rem 0.7rem; font-size:0.78rem; margin-bottom:0.5rem; margin-right:0.4rem; font-weight:600; }
    .doc-tag    { display:inline-block; background:#f0fdf4; border:1.5px solid #bbf7d0; color:#16a34a; border-radius:8px; padding:0.22rem 0.7rem; font-size:0.78rem; margin-bottom:0.5rem; margin-right:0.4rem; font-weight:600; }
    .doc-card   { background:linear-gradient(135deg,#fdf4ff,#eff6ff); border:1px solid #e9d5ff; border-radius:10px; padding:0.6rem 0.9rem; margin-bottom:0.4rem; font-size:0.81rem; color:#6d28d9; }

    /* Sidebar */
    .sidebar-title { color:#4c1d95; font-weight:700; font-size:0.86rem; margin-bottom:0.5rem; }
    .divider { border:none; border-top:1px solid #e9d5ff; margin:0.85rem 0; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg,#fdf4ff,#eff6ff) !important;
        color:#6d28d9 !important; border:1.5px solid #e9d5ff !important;
        border-radius:10px !important; font-weight:500 !important;
        font-size:0.82rem !important; width:100% !important;
        text-align:left !important; padding:0.45rem 0.75rem !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg,#f5f3ff,#dbeafe) !important;
        border-color:#c4b5fd !important; color:#4c1d95 !important;
    }
    h1,h2,h3 { color:#1e293b !important; }
    .stMarkdown p { color:#475569 !important; }
    .stSpinner > div { border-top-color: #a855f7 !important; }
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
    st.markdown('<div class="sidebar-title">📚 Study</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#a78bfa;font-size:0.75rem;margin-top:-0.3rem;">Powered by Groq · LLaMA 3.1</p>', unsafe_allow_html=True)
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
    <div class="hero-title"><span>Study</span></div>
    <div class="hero-sub">Ask anything — live scores, weather, news, or questions about your documents</div>
    <div class="pills">
        <div class="pill-purple">🌐 Live search</div>
        <div class="pill-blue">📄 Document Q&A</div>
        <div class="pill-green">🏏 Sports scores</div>
        <div class="pill-orange">🌦️ Weather</div>
        <div class="pill-pink">📝 Study help</div>
        {"<div class='pill-teal'>📎 " + str(doc_count) + " doc(s)</div>" if doc_count else ""}
        <div class="pill-teal">💬 {len(st.session_state.chats)} chat(s)</div>
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
