# from .base import RAGStrategy
# from search import secure_search

# class HybridRAG(RAGStrategy):
#     """
#     Hybrid RAG :
#     - recherche sémantique
#     - re-classement lexical
#     """

#     def retrieve(self, query, user_access_level="public"):
#         docs = secure_search(
#             query=query,
#             user_access_level=user_access_level,
#             k=10
#         )

#         keywords = query.lower().split()

#         def lexical_score(doc):
#             return sum(
#                 kw in doc.page_content.lower()
#                 for kw in keywords
#             )

#         ranked = sorted(
#             docs,
#             key=lexical_score,
#             reverse=True
#         )

#         return ranked[:3]

#     def build_prompt(self, query, documents):
#         context = "\n\n".join(
#             doc.page_content for doc in documents
#         )

#         return f"""
# You are a legal expert assistant.
# Answer strictly based on the clauses below.

# Clauses:
# {context}

# Question:
# {query}
# """.strip()
from .base import RAGStrategy
from search import secure_search
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

class HybridRAG(RAGStrategy):
    """
    Vrai Hybrid RAG :
    - recherche sémantique (dense) via secure_search
    - recherche lexicale (sparse) via BM25
    - fusion des scores via RRF
    - reranking final via cross-encoder
    """

    def __init__(self):
        # Cross-encoder pour le reranking final
        # self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
          self.reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
    # ─────────────────────────────────────────
    # ÉTAPE 1 : Recherche dense (sémantique)
    # ─────────────────────────────────────────
    def _dense_search(self, query, user_access_level, k=10):
        """
        Recherche par embeddings via secure_search.
        Retourne les docs triés par similarité sémantique.
        """
        return secure_search(
            query=query,
            user_access_level=user_access_level,
            k=k
        )

    # ─────────────────────────────────────────
    # ÉTAPE 2 : Recherche sparse (BM25)
    # ─────────────────────────────────────────
    def _sparse_search(self, query, docs, k=10):
        """
        Recherche lexicale BM25 sur les docs récupérés.
        BM25 prend en compte :
        - la fréquence du terme dans le doc
        - la rareté du terme dans tout le corpus
        - la longueur du doc
        """
        if not docs:
          return []
        # Tokenisation du corpus
        corpus = [doc.page_content.lower().split() for doc in docs]
        bm25 = BM25Okapi(corpus)

        # Tokenisation de la query
        tokenized_query = query.lower().split()

        # Score BM25 pour chaque doc
        scores = bm25.get_scores(tokenized_query)

        # Retourne les docs triés par score BM25
        scored_docs = sorted(
            zip(docs, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, score in scored_docs[:k]]

    # ─────────────────────────────────────────
    # ÉTAPE 3 : Fusion RRF
    # ─────────────────────────────────────────
    def _rrf_fusion(self, dense_docs, sparse_docs, k=60):
        """
        Reciprocal Rank Fusion — combine les deux classements.
        
        Formule : score(doc) = Σ 1 / (k + rang_i)
        
        k=60 est la constante standard qui évite de trop
        favoriser les docs en tête de chaque liste.
        """
        rrf_scores = {}

        # Score depuis le classement dense
        for rank, doc in enumerate(dense_docs):
            doc_id = doc.page_content  # identifiant unique du doc
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {"doc": doc, "score": 0}
            rrf_scores[doc_id]["score"] += 1 / (k + rank + 1)

        # Score depuis le classement sparse
        for rank, doc in enumerate(sparse_docs):
            doc_id = doc.page_content
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {"doc": doc, "score": 0}
            rrf_scores[doc_id]["score"] += 1 / (k + rank + 1)

        # Tri par score RRF décroissant
        sorted_docs = sorted(
            rrf_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        return [item["doc"] for item in sorted_docs]

    # ─────────────────────────────────────────
    # ÉTAPE 4 : Reranking cross-encoder
    # ─────────────────────────────────────────
    def _rerank(self, query, docs, top_n=3):
        """
        Cross-encoder réévalue chaque paire (query, doc)
        ensemble pour un score de pertinence plus précis.
        """
        # Prépare les paires (query, doc)
        pairs = [(query, doc.page_content) for doc in docs]

        # Score chaque paire
        scores = self.reranker.predict(pairs)

        # Trie par score décroissant
        ranked = sorted(
            zip(docs, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, score in ranked[:top_n]]

    # ─────────────────────────────────────────
    # PIPELINE PRINCIPAL
    # ─────────────────────────────────────────
    def retrieve(self, query, user_access_level="public"):

        # 1. Recherche dense
        dense_docs = self._dense_search(
            query, user_access_level, k=10
        )

        # 2. Recherche sparse BM25 sur le même corpus
        sparse_docs = self._sparse_search(
            query, dense_docs, k=10
        )

        # 3. Fusion RRF des deux classements
        fused_docs = self._rrf_fusion(dense_docs, sparse_docs)

        # 4. Reranking cross-encoder sur le top fusionné
        final_docs = self._rerank(query, fused_docs[:10], top_n=3)

        return final_docs

    # ─────────────────────────────────────────
    # PROMPT
    # ─────────────────────────────────────────
    def build_prompt(self, query, documents):
        # Balisage des docs pour traçabilité
        context = "\n\n".join(
            f"[DOC {i+1}] {doc.page_content}"
            for i, doc in enumerate(documents)
        )

        return f"""
You are a legal expert assistant.
Answer strictly based on the clauses below.
Cite the document number [DOC X] that supports each part of your answer.

Clauses:
{context}

Question:
{query}
""".strip()