import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from auth import create_jwt, decode_jwt
from auth_service import authenticate_user
from security import get_access_level_from_role
from factory import get_rag_strategy, get_llm
from pipeline import run_pipeline


# =============================
# Page config
# =============================
st.set_page_config(
    page_title="RAG Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# Custom CSS
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@300;400&display=swap');

:root {
    --bg-primary: #0c0d0f;
    --bg-secondary: #13151a;
    --bg-card: #181b22;
    --bg-elevated: #1e2229;
    --border: #2a2d35;
    --accent: #c8a96e;
    --accent-soft: rgba(200, 169, 110, 0.10);
    --accent-glow: rgba(200, 169, 110, 0.25);
    --text-primary: #f0ece4;
    --text-secondary: #b0b3bf;
    --text-muted: #7a7e8f;
    --font-display: 'Playfair Display', Georgia, serif;
    --font-body: 'DM Sans', system-ui, sans-serif;
    --font-mono: 'DM Mono', monospace;
}

html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.stApp { background-color: var(--bg-primary) !important; }

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 2.5rem 3.5rem !important;
    max-width: 860px !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
    width: 300px !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.5rem !important;
    max-width: none !important;
}

/* SIDEBAR BRAND */
.sidebar-brand {
    text-align: center;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.sidebar-brand h1 {
    font-family: var(--font-display) !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
    letter-spacing: 0.01em;
    margin: 0 !important;
}
.sidebar-brand p {
    font-size: 0.68rem;
    color: #9da1b0;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 0.4rem 0 0 0;
}

.section-label {
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9da1b0;
    margin-bottom: 0.9rem;
    margin-top: 1.5rem;
}

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label {
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #c0c3cf !important;
    margin-bottom: 0.4rem !important;
}

/* SELECTBOX */
.stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
.stSelectbox > div > div:hover { border-color: var(--accent) !important; }

/* BUTTONS */
.stButton > button {
    background-color: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    font-family: var(--font-body) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: var(--accent) !important;
    color: var(--bg-primary) !important;
    box-shadow: 0 4px 20px var(--accent-glow) !important;
    transform: translateY(-1px) !important;
}

/* PRIMARY ASK BUTTON */
.ask-btn .stButton > button {
    background-color: var(--accent) !important;
    color: var(--bg-primary) !important;
    font-size: 0.8rem !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 2px 14px var(--accent-glow) !important;
    margin-top: 0.5rem !important;
}
.ask-btn .stButton > button:hover {
    box-shadow: 0 6px 28px var(--accent-glow) !important;
    transform: translateY(-2px) !important;
}

hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ALERTS */
div[data-testid="stSuccess"] {
    background-color: rgba(74, 222, 128, 0.07) !important;
    border: 1px solid rgba(74, 222, 128, 0.2) !important;
    border-radius: 8px !important;
}
div[data-testid="stError"] {
    background-color: rgba(248, 113, 113, 0.07) !important;
    border: 1px solid rgba(248, 113, 113, 0.2) !important;
    border-radius: 8px !important;
}
div[data-testid="stWarning"] {
    background-color: rgba(251, 191, 36, 0.07) !important;
    border: 1px solid rgba(251, 191, 36, 0.2) !important;
    border-radius: 8px !important;
}

/* USER BADGE */
.user-badge {
    background-color: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0 1rem 0;
}
.badge-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 0;
}
.badge-row + .badge-row { border-top: 1px solid var(--border); }
.badge-key {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9da1b0;
}
.badge-val {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-primary);
    font-family: var(--font-mono);
}
.badge-val.accent { color: var(--accent); }

/* PAGE HEADER */
.page-header {
    margin-bottom: 3rem;
    padding-bottom: 2.5rem;
    border-bottom: 1px solid var(--border);
}
.page-tag {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    background-color: var(--accent-soft);
    border: 1px solid rgba(200, 169, 110, 0.22);
    border-radius: 4px;
    padding: 0.28rem 0.7rem;
    margin-bottom: 1.2rem;
}
.page-title {
    font-family: var(--font-display) !important;
    font-size: 2.6rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    line-height: 1.12 !important;
    letter-spacing: -0.025em !important;
    margin: 0 0 0.9rem 0 !important;
}
.page-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.7;
    max-width: 500px;
    font-weight: 300;
}

/* ANSWER CARD */
.answer-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem 2.2rem;
    margin: 2rem 0 1rem 0;
    position: relative;
    overflow: hidden;
}
.answer-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent) 0%, transparent 70%);
}
.answer-label {
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1.1rem;
}
.answer-text {
    font-size: 0.95rem;
    line-height: 1.85;
    color: var(--text-primary);
    font-weight: 300;
}

/* SOURCES */
.sources-header {
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #9da1b0;
    padding-top: 1.5rem;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    border-top: 1px solid var(--border);
}

/* EXPANDER */
.streamlit-expanderHeader {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    color: var(--text-secondary) !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease !important;
}
.streamlit-expanderHeader:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.streamlit-expanderContent {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1.2rem !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
    color: var(--text-secondary) !important;
}

/* QUESTION LABEL */
.question-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 0.6rem;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* SPINNER */
.stSpinner > div { border-top-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h1>RAG Intelligence</h1>
        <p>Secure Retrieval System</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Authentication</div>', unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")

    if st.button("Sign In"):
        role = authenticate_user(username, password)
        if role is None:
            st.error("Invalid credentials")
        else:
            token = create_jwt(username, role)
            st.session_state["jwt"] = token
            st.success("Access granted")

    st.markdown("---")

    if "jwt" in st.session_state:
        try:
            payload = decode_jwt(st.session_state["jwt"])
            user_role = payload["role"]
            user_access_level = get_access_level_from_role(user_role)

            st.markdown(f"""
            <div class="user-badge">
                <div class="badge-row">
                    <span class="badge-key">Identity</span>
                    <span class="badge-val accent">{payload['sub']}</span>
                </div>
                <div class="badge-row">
                    <span class="badge-key">Role</span>
                    <span class="badge-val">{user_role}</span>
                </div>
                <div class="badge-row">
                    <span class="badge-key">Access Level</span>
                    <span class="badge-val">{user_access_level}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)

            rag_strategy_name = st.selectbox(
                "RAG Strategy",
                ["simple", "secure", "hybrid", "modular"]
            )

            llm_name = st.selectbox(
                "Language Model",
                ["mistral", "qwen", "gemini", "llama"]
            )

            st.markdown("---")

            if st.button("Sign Out"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        except Exception:
            pass


# =============================
# MAIN CONTENT
# =============================
st.markdown("""
<div class="page-header">
    <div class="page-tag">Secure Retrieval-Augmented Generation</div>
    <div class="page-title">Ask your documents</div>
</div>
""", unsafe_allow_html=True)

# AUTH GATE
if "jwt" not in st.session_state:
    st.warning("Sign in via the sidebar to access the system.")
    st.stop()

try:
    payload = decode_jwt(st.session_state["jwt"])
except Exception as e:
    st.error(str(e))
    st.stop()

user_role = payload["role"]
user_access_level = get_access_level_from_role(user_role)

# QUESTION INPUT
st.markdown('<div class="question-label">Your Question</div>', unsafe_allow_html=True)
question = st.text_area(
    label="question_hidden",
    label_visibility="collapsed",
    placeholder="What would you like to know from the knowledge base?",
    height=140
)

st.markdown('<div class="ask-btn">', unsafe_allow_html=True)
ask_clicked = st.button("Submit Query")
st.markdown('</div>', unsafe_allow_html=True)

if ask_clicked:
    if not question.strip():
        st.warning("Please enter a question before submitting.")
    else:
        with st.spinner("Retrieving and synthesizing..."):
            rag = get_rag_strategy(rag_strategy_name)
            llm = get_llm(llm_name)

            answer, sources = run_pipeline(
                question=question,
                user_access_level=user_access_level,
                rag=rag,
                llm=llm
            )

        st.markdown(f"""
        <div class="answer-card">
            <div class="answer-label">Response</div>
            <div class="answer-text">{answer}</div>
        </div>
        """, unsafe_allow_html=True)

        if sources:
            st.markdown('<div class="sources-header">Retrieved Sources</div>', unsafe_allow_html=True)
            for i, doc in enumerate(sources, start=1):
                with st.expander(f"Source {i:02d}"):
                    st.write(doc.page_content)
                    st.json(doc.metadata)