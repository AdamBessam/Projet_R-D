import os
from dotenv import load_dotenv

# Load environment variables from .env file
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
    page_title="Secure RAG System",
    layout="wide"
)

st.title("🔐 Secure RAG Question Answering System")
st.markdown(
    """
Secure RAG system with **JWT-based authentication**.
User permissions are derived **automatically from identity**.
"""
)

# =============================
# SIDEBAR — LOGIN
# =============================
st.sidebar.header("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    role = authenticate_user(username, password)

    if role is None:
        st.sidebar.error("Invalid credentials")
    else:
        token = create_jwt(username, role)
        st.session_state["jwt"] = token
        st.sidebar.success("Authentication successful")

st.sidebar.markdown("---")

# =============================
# AUTH CHECK
# =============================
if "jwt" not in st.session_state:
    st.warning("Please authenticate to access the system.")
    st.stop()

try:
    payload = decode_jwt(st.session_state["jwt"])
except Exception as e:
    st.error(str(e))
    st.stop()

user_role = payload["role"]
user_access_level = get_access_level_from_role(user_role)

st.sidebar.info(f"👤 User: **{payload['sub']}**")
st.sidebar.info(f"Role: **{user_role}**")
st.sidebar.info(f"Access level: **{user_access_level}**")

# Logout button
if st.sidebar.button("🚪 Logout", type="primary"):
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.markdown("---")

# =============================
# SYSTEM CONFIG
# =============================
st.sidebar.header("⚙️ Configuration")

rag_strategy_name = st.sidebar.selectbox(
    "RAG strategy",
    ["simple", "secure", "hybrid", "modular"]
)

llm_name = st.sidebar.selectbox(
    "LLM model",
    ["ollama", "openai", "gemini"]
)

# =============================
# MAIN INPUT
# =============================
question = st.text_area(
    "❓ Enter your question",
    height=120
)

if st.button("🚀 Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Processing..."):
            rag = get_rag_strategy(rag_strategy_name)
            llm = get_llm(llm_name)

            answer, sources = run_pipeline(
                question=question,
                user_access_level=user_access_level,
                rag=rag,
                llm=llm
            )

            st.subheader("📌 Answer")
            st.write(answer)

            if sources:
                st.subheader("📚 Authorized sources")
                for i, doc in enumerate(sources, start=1):
                    with st.expander(f"Document {i}"):
                        st.write(doc.page_content)
                        st.json(doc.metadata)
