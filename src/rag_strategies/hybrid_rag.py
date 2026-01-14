from .base import RAGStrategy
from search import secure_search

class HybridRAG(RAGStrategy):
    """
    Hybrid RAG :
    - recherche sémantique
    - re-classement lexical
    """

    def retrieve(self, query, user_access_level):
        docs = secure_search(
            query=query,
            user_access_level=user_access_level,
            k=10
        )

        keywords = query.lower().split()

        def lexical_score(doc):
            return sum(
                kw in doc.page_content.lower()
                for kw in keywords
            )

        ranked = sorted(
            docs,
            key=lexical_score,
            reverse=True
        )

        return ranked[:3]

    def build_prompt(self, query, documents):
        context = "\n\n".join(
            doc.page_content for doc in documents
        )

        return f"""
You are a legal expert assistant.
Answer strictly based on the clauses below.

Clauses:
{context}

Question:
{query}
""".strip()
