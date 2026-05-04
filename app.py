import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun
import subprocess, io, re, json, os
from datetime import datetime
import pdfplumber
import docx

NOTES_FILE = "notes.json"

st.set_page_config(page_title="Study", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(160deg, #fdf4ff 0%, #eff6ff 35%, #f0fdf4 65%, #fff7ed 100%);
        min-height: 100vh;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fdf4ff 0%, #eff6ff 100%);
        border-right: 1px solid #e9d5ff;
    }

    .hero { text-align:center; padding:1.5rem 1rem 0.6rem; }
    .hero-badge { display:inline-block; background:linear-gradient(90deg,#a855f7,#3b82f6,#06b6d4); color:white; font-size:0.68rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; padding:0.25rem 0.85rem; border-radius:50px; margin-bottom:0.6rem; }
    .hero-title { font-size:2.8rem; font-weight:800; margin:0 0 0.3rem; background:linear-gradient(90deg,#a855f7,#3b82f6,#10b981); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .hero-sub { color:#6b7280; font-size:0.9rem; margin-bottom:0.7rem; }

    .pills { display:flex; justify-content:center; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.8rem; }
    .pill-purple { background:#fdf4ff; border:1.5px solid #e9d5ff; color:#7c3aed; border-radius:50px; padding:0.25rem 0.8rem; font-size:0.75rem; font-weight:600; }
    .pill-blue   { background:#eff6ff; border:1.5px solid #bfdbfe; color:#2563eb; border-radius:50px; padding:0.25rem 0.8rem; font-size:0.75rem; font-weight:600; }
    .pill-green  { background:#f0fdf4; border:1.5px solid #bbf7d0; color:#16a34a; border-radius:50px; padding:0.25rem 0.8rem; font-size:0.75rem; font-weight:600; }
    .pill-orange { background:#fff7ed; border:1.5px solid #fed7aa; color:#ea580c; border-radius:50px; padding:0.25rem 0.8rem; font-size:0.75rem; font-weight:600; }
    .pill-pink   { background:#fdf2f8; border:1.5px solid #fbcfe8; color:#db2777; border-radius:50px; padding:0.25rem 0.8rem; font-size:0.75rem; font-weight:600; }
    .pill-teal   { background:#f0fdfa; border:1.5px solid #99f6e4; color:#0f766e; border-radius:50px; padding:0.25rem 0.8rem; font-size:0.75rem; font-weight:600; }

    [data-testid="stChatMessageContent"] {
        background:linear-gradient(135deg,#f0fdf4,#eff6ff) !important;
        border:1.5px solid #bbf7d0 !important; border-radius:18px !important;
        color:#1e293b !important; padding:0.9rem 1.1rem !important;
        font-size:0.93rem !important; line-height:1.72 !important;
        box-shadow:0 2px 8px rgba(16,185,129,0.07) !important;
    }
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li { color:#334155 !important; }
    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] b { color:#7c3aed !important; }
    [data-testid="stChatMessageContent"] code { background:#fdf4ff; color:#7c3aed; padding:0.1rem 0.4rem; border-radius:4px; font-size:0.87rem; }
    [data-testid="stChatMessageContent"] h1,
    [data-testid="stChatMessageContent"] h2,
    [data-testid="stChatMessageContent"] h3 { color:#1e293b !important; margin-top:0.7rem; }
    [data-testid="stChatMessageContent"] blockquote { border-left:3px solid #a855f7; padding-left:0.75rem; color:#6b7280 !important; }

    .stChatInputContainer {
        background:linear-gradient(135deg,#fdf4ff,#eff6ff) !important;
        border:1.5px solid #e9d5ff !important; border-radius:18px !important;
        box-shadow:0 4px 16px rgba(168,85,247,0.1) !important;
    }
    .stChatInputContainer textarea { color:#1e293b !important; font-size:0.93rem !important; background:transparent !important; }
    .stChatInputContainer textarea::placeholder { color:#a78bfa !important; }

    .source-tag { display:inline-block; background:#eff6ff; border:1.5px solid #bfdbfe; color:#2563eb; border-radius:8px; padding:0.2rem 0.65rem; font-size:0.77rem; margin-bottom:0.45rem; margin-right:0.35rem; font-weight:600; }
    .doc-tag    { display:inline-block; background:#f0fdf4; border:1.5px solid #bbf7d0; color:#16a34a; border-radius:8px; padding:0.2rem 0.65rem; font-size:0.77rem; margin-bottom:0.45rem; margin-right:0.35rem; font-weight:600; }

    .note-card { background:linear-gradient(135deg,#fdf4ff,#fff7ed); border:1.5px solid #e9d5ff; border-radius:14px; padding:0.85rem 1rem; margin-bottom:0.7rem; }
    .note-title { font-weight:700; color:#6d28d9; font-size:0.9rem; margin-bottom:0.3rem; }
    .note-date  { font-size:0.72rem; color:#94a3b8; margin-bottom:0.4rem; }
    .note-body  { font-size:0.87rem; color:#374151; line-height:1.6; }

    .doc-card { background:linear-gradient(135deg,#fdf4ff,#eff6ff); border:1px solid #e9d5ff; border-radius:10px; padding:0.55rem 0.85rem; margin-bottom:0.35rem; font-size:0.8rem; color:#6d28d9; }

    .model-badge { display:inline-block; background:linear-gradient(90deg,#a855f7,#3b82f6); color:white; border-radius:8px; padding:0.18rem 0.6rem; font-size:0.75rem; font-weight:600; margin-left:0.4rem; }

    .sidebar-title { color:#4c1d95; font-weight:700; font-size:0.85rem; margin-bottom:0.45rem; }
    .divider { border:none; border-top:1px solid #e9d5ff; margin:0.8rem 0; }

    .stButton > button {
        background:linear-gradient(135deg,#fdf4ff,#eff6ff) !important;
        color:#6d28d9 !important; border:1.5px solid #e9d5ff !important;
        border-radius:10px !important; font-weight:500 !important;
        font-size:0.81rem !important; width:100% !important;
        text-align:left !important; padding:0.4rem 0.7rem !important;
    }
    .stButton > button:hover { background:linear-gradient(135deg,#f5f3ff,#dbeafe) !important; border-color:#c4b5fd !important; color:#4c1d95 !important; }

    .stTabs [data-baseweb="tab-list"] { background:linear-gradient(135deg,#fdf4ff,#eff6ff); border-radius:12px; padding:0.2rem; border:1.5px solid #e9d5ff; }
    .stTabs [data-baseweb="tab"] { border-radius:10px; font-weight:600; color:#6d28d9; }
    .stTabs [aria-selected="true"] { background:linear-gradient(90deg,#a855f7,#3b82f6) !important; color:white !important; }

    .stTextArea textarea { background:#fdf4ff !important; border:1.5px solid #e9d5ff !important; border-radius:12px !important; color:#1e293b !important; }
    .stSelectbox > div > div { background:linear-gradient(135deg,#fdf4ff,#eff6ff) !important; border:1.5px solid #e9d5ff !important; color:#6d28d9 !important; border-radius:10px !important; }

    h1,h2,h3,h4 { color:#1e293b !important; }
    .stMarkdown p { color:#475569 !important; }
    .stSpinner > div { border-top-color:#a855f7 !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")[1:]
        models = [l.split()[0] for l in lines if l.strip() and "embed" not in l.lower()]
        return models if models else ["llama3"]
    except Exception:
        return ["llama3"]

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

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

LIVE_KEYWORDS = re.compile(
    r"\b(score|scores|ipl|cricket|football|match|live|weather|temperature|forecast|"
    r"today|tonight|right now|currently|latest|news|stock|price|rate|exchange|"
    r"trending|update|breaking|win|won|lost|playing|result|standings|"
    r"premier league|nba|nfl|f1|grand prix|election|inflation|rainfall|humidity)\b",
    re.IGNORECASE
)

def is_live_query(text):
    return bool(LIVE_KEYWORDS.search(text))

# ── Session defaults ──────────────────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"
if "docs" not in st.session_state:
    st.session_state.docs = {}
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama3:latest"

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

search = DuckDuckGoSearchRun()

SYSTEM = SystemMessage(content="""You are a sharp, concise AI assistant for studying and daily use.

Rules:
- Keep answers SHORT and to the point. No fluff, no padding.
- Max 5 bullet points unless more are truly needed.
- Use bold for key terms only. Skip headers for short answers.
- For facts/live data: one clear sentence per fact at the top.
- For explanations: 2-4 sentences max, then bullets if needed.
- Never repeat the question. Never say "Great question!" or filler phrases.
- If asked something simple, give a simple answer — one or two lines is fine.""")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">📚 Study</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#a78bfa;font-size:0.74rem;margin-top:-0.3rem;">Local AI · 100% Free · No limits</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Model selector
    st.markdown('<div class="sidebar-title">🤖 Model</div>', unsafe_allow_html=True)
    available_models = get_ollama_models()
    model_labels = {
        "llama3:latest":    "🦙 LLaMA 3 (4.7GB) — General",
        "deepseek-r1:8b":   "🧠 DeepSeek-R1 8B — Reasoning",
        "phi4-mini:latest": "⚡ Phi-4 Mini 3.8B — Fast",
        "phi4-mini":        "⚡ Phi-4 Mini 3.8B — Fast",
    }
    display = [model_labels.get(m, m) for m in available_models]
    idx = 0
    if st.session_state.selected_model in available_models:
        idx = available_models.index(st.session_state.selected_model)
    chosen_display = st.selectbox("Model", display, index=idx, label_visibility="collapsed")
    st.session_state.selected_model = available_models[display.index(chosen_display)]

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # New chat
    if st.button("✏️  New Chat"):
        new_chat()
        st.rerun()

    # Chat list
    st.markdown('<div class="sidebar-title" style="margin-top:0.5rem;">💬 Chats</div>', unsafe_allow_html=True)
    for chat_name in list(st.session_state.chats.keys()):
        is_active = chat_name == st.session_state.active_chat
        count = len(st.session_state.chats[chat_name])
        c1, c2 = st.columns([0.78, 0.22])
        with c1:
            label = f"{'● ' if is_active else ''}{chat_name} ({count})"
            if st.button(label, key=f"chat_{chat_name}"):
                st.session_state.active_chat = chat_name
                st.rerun()
        with c2:
            if len(st.session_state.chats) > 1:
                if st.button("✕", key=f"dc_{chat_name}"):
                    del st.session_state.chats[chat_name]
                    st.session_state.active_chat = list(st.session_state.chats.keys())[0]
                    st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Documents
    st.markdown('<div class="sidebar-title">📎 Upload Files</div>', unsafe_allow_html=True)
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
            if st.button("✕", key=f"dd_{fname}"):
                del st.session_state.docs[fname]
                st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️  Clear This Chat"):
        st.session_state.chats[st.session_state.active_chat] = []
        st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
doc_count = len(st.session_state.docs)
model_short = st.session_state.selected_model.split(":")[0]

st.markdown(f"""
<div class="hero">
    <div class="hero-badge">Ollama · Local · Free · No Limits</div>
    <div class="hero-title">Study</div>
    <div class="hero-sub">Your personal AI — studying, daily questions, live search & document Q&A</div>
    <div class="pills">
        <div class="pill-purple">🤖 {model_short}</div>
        <div class="pill-blue">🌐 Live search</div>
        <div class="pill-green">📄 Document Q&A</div>
        <div class="pill-orange">📝 Notes</div>
        <div class="pill-pink">🏏 Sports & Weather</div>
        {"<div class='pill-teal'>📎 " + str(doc_count) + " file(s)</div>" if doc_count else ""}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_notes = st.tabs(["💬 Chat", "📝 My Notes"])

# ════════════════════════════════════════════════════════════════════════
# CHAT TAB
# ════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown(f"**{st.session_state.active_chat}** &nbsp;<span class='model-badge'>{model_short}</span>", unsafe_allow_html=True)

    for msg in current_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Auto-scroll to bottom
    st.markdown("""
    <script>
        const chatContainer = window.parent.document.querySelector('[data-testid="stVerticalBlock"]');
        if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
        window.parent.document.querySelector('.main').scrollTo(0, window.parent.document.querySelector('.main').scrollHeight);
    </script>
    """, unsafe_allow_html=True)

    prompt = st.session_state.pop("quick_prompt", None)
    user_input = st.chat_input("Ask anything — study help, live scores, weather, summarise my doc...")
    if user_input:
        prompt = user_input

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        current_messages().append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            use_web = is_live_query(prompt)
            has_docs = bool(st.session_state.docs)
            doc_query = any(w in prompt.lower() for w in ["document","doc","uploaded","file","summarise","summary","quiz","notes","pdf"])

            # Medium memory: last 10 messages
            llm = ChatOllama(model=st.session_state.selected_model, temperature=0.3, num_predict=512)
            messages = [SYSTEM]
            for m in current_messages()[:-1][-10:]:
                cls = HumanMessage if m["role"] == "user" else AIMessage
                messages.append(cls(content=m["content"]))

            tags_html = ""

            if use_web:
                tags_html += '<span class="source-tag">🌐 Live search</span>'
                with st.spinner("Searching the web..."):
                    web_data = search.run(prompt)
                messages.append(HumanMessage(content=f"Question: {prompt}\n\nLive results:\n{web_data}\n\nAnswer using these. Put key facts first."))

            elif has_docs and (doc_query or not use_web):
                tags_html += '<span class="doc-tag">📄 Using your files</span>'
                combined = "\n\n---\n\n".join([f"[{n}]\n{t[:4000]}" for n, t in st.session_state.docs.items()])
                messages.append(HumanMessage(content=f"Files:\n{combined}\n\nQuestion: {prompt}"))

            else:
                messages.append(HumanMessage(content=prompt))

            if tags_html:
                st.markdown(tags_html, unsafe_allow_html=True)

            with st.spinner(f"Thinking with {model_short}..."):
                response = llm.invoke(messages)

            st.markdown(response.content)
            current_messages().append({"role": "assistant", "content": response.content})

            # Scroll to bottom after response
            st.markdown("""
            <script>
                window.parent.document.querySelector('.main').scrollTo(0, window.parent.document.querySelector('.main').scrollHeight);
            </script>
            """, unsafe_allow_html=True)

            # Save to notes button
            if st.button("⭐ Save this to Notes", key=f"save_{len(current_messages())}"):
                notes = load_notes()
                notes.append({
                    "title": prompt[:60] + ("..." if len(prompt) > 60 else ""),
                    "content": response.content,
                    "date": datetime.now().strftime("%d %b %Y, %H:%M"),
                    "model": model_short
                })
                save_notes(notes)
                st.success("Saved to Notes!")

# ════════════════════════════════════════════════════════════════════════
# NOTES TAB
# ════════════════════════════════════════════════════════════════════════
with tab_notes:
    notes = load_notes()

    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        st.markdown("### 📝 My Saved Notes")
    with col_r:
        if notes and st.button("🗑️ Clear All Notes"):
            save_notes([])
            st.rerun()

    # Add new note manually
    with st.expander("➕ Add a new note", expanded=False):
        new_title = st.text_input("Title", placeholder="e.g. Photosynthesis key points")
        new_body  = st.text_area("Content", placeholder="Paste or type your notes here...", height=150)
        if st.button("💾 Save Note"):
            if new_title.strip() or new_body.strip():
                notes = load_notes()
                notes.append({
                    "title": new_title.strip() or "Untitled",
                    "content": new_body.strip(),
                    "date": datetime.now().strftime("%d %b %Y, %H:%M"),
                    "model": "manual"
                })
                save_notes(notes)
                st.success("Note saved!")
                st.rerun()

    if not notes:
        st.info("No notes yet. Ask something in the chat and click ⭐ Save this to Notes, or add one manually above.")
    else:
        # Search notes
        search_q = st.text_input("🔍 Search notes", placeholder="Filter by keyword...", label_visibility="collapsed")
        filtered = [n for n in reversed(notes) if not search_q or search_q.lower() in n.get("title","").lower() or search_q.lower() in n.get("content","").lower()]

        for i, note in enumerate(filtered):
            real_idx = notes.index(note)
            with st.expander(f"📌 {note.get('title','Untitled')}  —  {note.get('date','')}"):
                edited = st.text_area("Edit note", value=note.get("content",""), height=200, key=f"note_edit_{i}")
                c1, c2 = st.columns([0.5, 0.5])
                with c1:
                    if st.button("💾 Update", key=f"upd_{i}"):
                        notes[real_idx]["content"] = edited
                        save_notes(notes)
                        st.success("Updated!")
                        st.rerun()
                with c2:
                    if st.button("🗑️ Delete", key=f"del_note_{i}"):
                        notes.pop(real_idx)
                        save_notes(notes)
                        st.rerun()
