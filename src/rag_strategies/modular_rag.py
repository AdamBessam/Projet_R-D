from .base import RAGStrategy
from search import secure_search

class ModularRAG(RAGStrategy):
    """
    RAG expérimental servant de point d'extension :
    - prêt pour multi-steps
    - prêt pour query rewriting
    """

    def retrieve(self, query, user_access_level):
        # étape 1 : recherche large
        docs = secure_search(
            query=query,
            user_access_level=user_access_level,
            k=8
        )

        # étape 2 (placeholder) : filtrage futur
        return docs[:3]

    def build_prompt(self, query, documents):
        context = "\n\n".join(
            f"[DOC] {doc.page_content}"
            for doc in documents
        )

        return f"""
You are an experimental RAG system.
Use only the information below.

Documents:
{context}

Question:
{query}
""".strip()
