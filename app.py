import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os, io, json, webbrowser
import pdfplumber
import docx

load_dotenv()

st.set_page_config(page_title="AI Job Agent", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #f5f7fa; }
    section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }

    .hero-container { text-align: center; padding: 2rem 1rem 1rem; }
    .hero-badge { display: inline-block; background: linear-gradient(90deg,#6366f1,#06b6d4); color:white; font-size:0.72rem; font-weight:600; letter-spacing:2px; text-transform:uppercase; padding:0.3rem 1rem; border-radius:50px; margin-bottom:1rem; }
    .hero-title { font-size:2.4rem; font-weight:700; color:#1e293b; margin:0 0 0.4rem; line-height:1.2; }
    .hero-title span { background:linear-gradient(90deg,#6366f1,#06b6d4); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .hero-subtitle { color:#64748b; font-size:1rem; margin-bottom:0.5rem; }
    .stats-row { display:flex; justify-content:center; gap:1.2rem; margin:1.2rem 0; flex-wrap:wrap; }
    .stat-pill { background:#fff; border:1px solid #e2e8f0; border-radius:50px; padding:0.35rem 1rem; color:#475569; font-size:0.82rem; font-weight:500; box-shadow:0 1px 3px rgba(0,0,0,0.06); }
    .stat-pill b { color:#6366f1; }

    .job-card {
        background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px;
        padding: 1.1rem 1.3rem; margin-bottom: 0.8rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05); transition: border-color 0.2s;
    }
    .job-card:hover { border-color: #6366f1; }
    .job-card.selected { border-color: #6366f1; background: #fafaff; }
    .job-title { font-size:1rem; font-weight:700; color:#1e293b; margin-bottom:0.2rem; }
    .job-meta { font-size:0.82rem; color:#64748b; margin-bottom:0.5rem; }
    .job-meta b { color:#6366f1; }
    .job-desc { font-size:0.88rem; color:#475569; line-height:1.55; }
    .job-salary { display:inline-block; background:#f0fdf4; border:1px solid #bbf7d0; color:#16a34a; border-radius:6px; padding:0.15rem 0.6rem; font-size:0.78rem; font-weight:600; margin-top:0.4rem; }
    .applied-badge { display:inline-block; background:#eff6ff; border:1px solid #bfdbfe; color:#3b82f6; border-radius:6px; padding:0.15rem 0.6rem; font-size:0.78rem; font-weight:600; margin-left:0.5rem; }

    .cv-card { background:linear-gradient(135deg,#eff6ff,#f0fdf4); border:1px solid #bfdbfe; border-radius:12px; padding:0.75rem 1rem; margin-bottom:0.5rem; font-size:0.83rem; color:#1e40af; }
    .search-tag { display:inline-block; background:#eff6ff; border:1px solid #bfdbfe; color:#3b82f6; border-radius:8px; padding:0.25rem 0.7rem; font-size:0.82rem; margin-bottom:0.5rem; }
    .cv-tag { display:inline-block; background:#f0fdf4; border:1px solid #bbf7d0; color:#16a34a; border-radius:8px; padding:0.25rem 0.7rem; font-size:0.82rem; margin-bottom:0.5rem; margin-left:0.4rem; }

    [data-testid="stChatMessageContent"] { background:#fff !important; border:1px solid #e2e8f0 !important; border-radius:16px !important; color:#1e293b !important; padding:1rem 1.2rem !important; font-size:0.95rem !important; line-height:1.65 !important; box-shadow:0 1px 4px rgba(0,0,0,0.05) !important; }
    [data-testid="stChatMessageContent"] p, [data-testid="stChatMessageContent"] li { color:#334155 !important; }
    [data-testid="stChatMessageContent"] strong, [data-testid="stChatMessageContent"] b { color:#6366f1 !important; }

    .stChatInputContainer { background:#fff !important; border:1.5px solid #e2e8f0 !important; border-radius:16px !important; box-shadow:0 2px 8px rgba(0,0,0,0.06) !important; }
    .stChatInputContainer textarea { color:#1e293b !important; font-size:0.95rem !important; }
    .stChatInputContainer textarea::placeholder { color:#94a3b8 !important; }

    .sidebar-title { color:#1e293b; font-weight:600; font-size:0.88rem; margin-bottom:0.6rem; }
    .divider { border:none; border-top:1px solid #f1f5f9; margin:1rem 0; }
    .tag-chip { display:inline-block; background:#f1f5f9; border:1px solid #e2e8f0; color:#475569; border-radius:50px; padding:0.2rem 0.65rem; font-size:0.78rem; margin:0.2rem 0.15rem 0.2rem 0; }

    h1,h2,h3 { color:#1e293b !important; }
    .stMarkdown p { color:#475569 !important; }
    .stButton > button { background:#f8fafc !important; color:#334155 !important; border:1px solid #e2e8f0 !important; border-radius:10px !important; font-weight:500 !important; font-size:0.85rem !important; width:100% !important; text-align:left !important; }
    .stButton > button:hover { background:#eff6ff !important; border-color:#bfdbfe !important; color:#3b82f6 !important; }

    .tracker-header { font-size:0.9rem; font-weight:600; color:#1e293b; margin-bottom:0.5rem; }
    .tracker-item { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.5rem 0.75rem; margin-bottom:0.4rem; font-size:0.82rem; color:#475569; }
    .tracker-item b { color:#6366f1; }
</style>
""", unsafe_allow_html=True)

# ── File parsing ──────────────────────────────────────────────────────────────
def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    if name.endswith(".pdf"):
        text = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
        return "\n".join(text)
    elif name.endswith(".docx"):
        doc = docx.Document(io.BytesIO(data))
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    else:
        return data.decode("utf-8", errors="ignore")

# ── LLM + Search ──────────────────────────────────────────────────────────────
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
search_tool = DuckDuckGoSearchRun()

def parse_jobs_from_results(search_result: str, user_prompt: str, cv_text: str) -> list:
    cv_context = f"\nUser CV:\n{cv_text[:1500]}" if cv_text else ""
    response = llm.invoke([
        SystemMessage(content=f"""Extract job listings from the search results and return a JSON array.
Each job must have: title, company, location, salary (or empty string), description (1-2 sentences), url (direct apply link if found, else construct a reed.co.uk search URL).
Return ONLY valid JSON array, no markdown, no explanation.{cv_context}"""),
        HumanMessage(content=f"User searched for: {user_prompt}\n\nSearch results:\n{search_result}")
    ])
    try:
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return []

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in [("messages", []), ("job_listings", []), ("applied_jobs", []), ("selected_jobs", set())]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">💼 AI Job Agent</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;font-size:0.78rem;margin-top:-0.3rem;">Powered by Groq · LLaMA 3</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">📄 Upload Your CV</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("PDF, DOCX, TXT, CSV", type=["pdf","docx","txt","csv"], label_visibility="collapsed")
    if uploaded_file:
        if st.session_state.get("cv_filename") != uploaded_file.name:
            with st.spinner("Reading CV..."):
                st.session_state.cv_text = extract_text(uploaded_file)
                st.session_state.cv_filename = uploaded_file.name
        st.markdown(f'<div class="cv-card">✅ <b>{uploaded_file.name}</b><br><span style="color:#3b82f6">{len(st.session_state.get("cv_text",""))} chars loaded</span></div>', unsafe_allow_html=True)
        if st.button("🗑️ Remove CV"):
            st.session_state.pop("cv_text", None)
            st.session_state.pop("cv_filename", None)
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">⚡ Quick Searches</div>', unsafe_allow_html=True)
    for qs in ["Python Developer London","Remote Data Analyst","Frontend React Engineer","Machine Learning Engineer","DevOps AWS Remote","Product Manager Tech"]:
        if st.button(qs, key=f"qs_{qs}"):
            st.session_state["quick_prompt"] = qs

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔥 Popular Skills</div>', unsafe_allow_html=True)
    skills = ["Python","React","AWS","SQL","Docker","Node.js","Kubernetes","TypeScript"]
    st.markdown(" ".join([f'<span class="tag-chip">{s}</span>' for s in skills]), unsafe_allow_html=True)

    # Application tracker
    if st.session_state.applied_jobs:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(f'<div class="tracker-header">📋 Applied Jobs ({len(st.session_state.applied_jobs)})</div>', unsafe_allow_html=True)
        for job in st.session_state.applied_jobs[-5:]:
            st.markdown(f'<div class="tracker-item"><b>{job["title"]}</b><br>{job["company"]} · {job["location"]}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.job_listings = []
        st.rerun()

# ── Hero ──────────────────────────────────────────────────────────────────────
cv_loaded = bool(st.session_state.get("cv_text"))
st.markdown(f"""
<div class="hero-container">
    <div class="hero-badge">AI-Powered · Live Job Search & Apply</div>
    <div class="hero-title">Find & Apply to Your <span>Dream Job</span></div>
    <div class="hero-subtitle">{"CV loaded — I'll match and apply to jobs for you!" if cv_loaded else "Upload your CV or type keywords — search, select, and apply in one click"}</div>
    <div class="stats-row">
        <div class="stat-pill">🇬🇧 <b>Indeed UK</b> & Reed UK</div>
        <div class="stat-pill">⚡ <b>Real-time</b> results</div>
        <div class="stat-pill">🖱️ <b>One-click</b> apply</div>
        {"<div class='stat-pill'>📄 <b>CV</b> loaded</div>" if cv_loaded else ""}
        {f"<div class='stat-pill'>✅ <b>{len(st.session_state.applied_jobs)}</b> applied</div>" if st.session_state.applied_jobs else ""}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Job cards ─────────────────────────────────────────────────────────────────
if st.session_state.job_listings:
    st.markdown("---")
    st.markdown("### 🎯 Job Listings — Select & Apply")

    selected = []
    for i, job in enumerate(st.session_state.job_listings):
        already_applied = any(a["title"] == job["title"] and a["company"] == job["company"] for a in st.session_state.applied_jobs)
        col1, col2 = st.columns([0.07, 0.93])
        with col1:
            checked = st.checkbox("", key=f"job_check_{i}", value=already_applied, disabled=already_applied)
        with col2:
            applied_html = '<span class="applied-badge">✅ Applied</span>' if already_applied else ""
            salary_html = f'<div class="job-salary">💰 {job.get("salary","")}</div>' if job.get("salary") else ""
            st.markdown(f"""
            <div class="job-card {'selected' if checked else ''}">
                <div class="job-title">{job.get("title","N/A")} {applied_html}</div>
                <div class="job-meta"><b>{job.get("company","Unknown")}</b> &nbsp;·&nbsp; 📍 {job.get("location","UK")}</div>
                <div class="job-desc">{job.get("description","")}</div>
                {salary_html}
            </div>
            """, unsafe_allow_html=True)
        if checked and not already_applied:
            selected.append(job)

    if selected:
        st.markdown(f"**{len(selected)} job(s) selected**")
        if st.button(f"🚀 Apply to {len(selected)} Selected Job(s)", type="primary"):
            for job in selected:
                url = job.get("url", "")
                if not url or not url.startswith("http"):
                    query = f"{job.get('title','')} {job.get('company','')}".replace(" ", "+")
                    url = f"https://www.reed.co.uk/jobs/{query}"
                webbrowser.open(url)
                if job not in st.session_state.applied_jobs:
                    st.session_state.applied_jobs.append(job)
            st.success(f"✅ Opened {len(selected)} application(s) in your browser!")
            st.rerun()

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.session_state.pop("quick_prompt", None)
chat_input = st.chat_input("Say hello or type a job role, e.g. Python developer London...")
if chat_input:
    prompt = chat_input

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    cv_text = st.session_state.get("cv_text", "")
    cv_context = f"\n\nUser CV:\n{cv_text[:3000]}" if cv_text else ""

    system = SystemMessage(content=f"""You are a friendly AI Job Agent assistant.
- For greetings or general conversation: respond naturally.
- For job searches: confirm you're searching and mention how many results you found.
- Always be concise and friendly.{cv_context}""")

    intent_check = llm.invoke([
        SystemMessage(content="Reply ONLY with 'SEARCH' if the message is about finding jobs, roles, careers, or says find/search/apply. Reply 'CHAT' for everything else."),
        HumanMessage(content=prompt)
    ])

    with st.chat_message("assistant"):
        if "SEARCH" in intent_check.content.strip().upper():
            if cv_text:
                kw_response = llm.invoke([
                    SystemMessage(content="Extract best job search keywords from CV and request. Return only a short query (max 8 words)."),
                    HumanMessage(content=f"CV:\n{cv_text[:2000]}\n\nRequest: {prompt}")
                ])
                search_query = kw_response.content.strip()
            else:
                search_query = prompt

            st.markdown(f'<div class="search-tag">🔍 Searching: {search_query}</div>' +
                        (f'<div class="cv-tag">📄 Using your CV</div>' if cv_text else ""),
                        unsafe_allow_html=True)

            with st.spinner("Finding live job listings..."):
                search_result = search_tool.run(f"{search_query} jobs site:indeed.co.uk OR site:reed.co.uk")
                jobs = parse_jobs_from_results(search_result, search_query, cv_text)
                st.session_state.job_listings = jobs

                reply = f"Found **{len(jobs)} job listings** for **{search_query}**! Select the ones you like below and click **Apply** to open the applications."
                if not jobs:
                    reply = f"I searched for **{search_query}** but couldn't extract structured listings. Try rephrasing your search."
        else:
            reply = llm.invoke([system, HumanMessage(content=prompt)]).content

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    st.rerun()
