from .base import RAGStrategy
from search import secure_search

class SimpleRAG(RAGStrategy):
    """
    RAG simple basé uniquement sur la recherche sémantique.
    """

    def retrieve(self, query, user_access_level="public", k=5):
        return secure_search(
            query=query,
            user_access_level=user_access_level,
            k=k
        )

    def build_prompt(self, query, documents):
        context = "\n\n".join(doc.page_content for doc in documents)

        return f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{query}
""".strip()
