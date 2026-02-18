from .base import RAGStrategy
from search import secure_search

class SecureRAG(RAGStrategy):
    """
    RAG avec sécurité renforcée :
    - refus explicite
    - pas de génération sans documents autorisés
    """
    
    def __init__(self, llm=None, user_access_level="public"):
        super().__init__(llm)
        self.default_access_level = user_access_level

    def retrieve(self, query, user_access_level="public", k=5):
        documents = secure_search(
            query=query,
            user_access_level=user_access_level,
            k=k
        )

        if not documents:
            return []

        return documents

    def build_prompt(self, query, documents):
        context = "\n\n".join(
            f"- {doc.page_content}"
            for doc in documents
        )

        return f"""
You are a secure legal assistant.
Use ONLY the clauses below.
If information is missing, explicitly say you do not know.

Authorized clauses:
{context}

Question:
{query}
""".strip()
