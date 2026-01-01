import streamlit as st

from rag import rag_answer
from search import secure_search

st.set_page_config(
    page_title="Secure RAG Demo",
    layout="centered"
)

st.title("🔐 Secure RAG Demonstration")
st.markdown(
    """
This application demonstrates a **Retrieval-Augmented Generation (RAG)** system
with **access control** applied *before* any language model generation.
"""
)

# ================= USER INPUT =================
question = st.text_input(
    "Enter your question:",
    placeholder="e.g. What are the payment terms?"
)

user_access_level = st.selectbox(
    "Select user access level:",
    ["public", "internal", "confidential"]
)

k = st.slider(
    "Number of retrieved documents:",
    min_value=1,
    max_value=5,
    value=3
)

submit = st.button("Submit query")

# ================= PROCESS =================
if submit and question:
    with st.spinner("Processing request..."):
        # 1️⃣ Recherche sécurisée
        documents = secure_search(
            query=question,
            user_access_level=user_access_level,
            k=k
        )

        if not documents:
            st.warning("No authorized information allows answering this question.")
        else:
            # 2️⃣ Génération RAG
            answer = rag_answer(
                question=question,
                user_access_level=user_access_level,
                k=k
            )

            st.success("Answer generated successfully!")
            st.markdown("### 💬 Generated Answer")
            st.write(answer)

            # ================= SOURCES =================
            with st.expander("📄 View authorized source documents"):
                for i, doc in enumerate(documents, 1):
                    st.markdown(f"**Document {i}**")
                    st.markdown(f"- Access level: `{doc.metadata.get('access_level')}`")
                    st.markdown(doc.page_content)
                    st.markdown("---")

elif submit:
    st.warning("Please enter a question.")
