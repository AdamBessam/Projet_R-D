import requests
from src.search import secure_search

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


def build_prompt(question, documents):
    context = "\n\n".join(
        f"- {doc.page_content}" for doc in documents
    )

    return f"""
You are a legal document assistant.

Answer the question ONLY using the contract clauses below.
If the information is not present, say you do not know.

Contract clauses:
{context}

Question:
{question}
""".strip()


def call_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 2048
            }
        },
        timeout=400
    )
    response.raise_for_status()
    return response.json()["response"]


def rag_answer(question, user_access_level, k=5):
    # 1️⃣ Recherche sécurisée
    documents = secure_search(
        query=question,
        user_access_level=user_access_level,
        k=k
    )

    if not documents:
        return "No authorized information allows answering this question."

    # 2️⃣ Prompt contrôlé
    prompt = build_prompt(question, documents)

    # 3️⃣ Génération locale
    return call_ollama(prompt)
