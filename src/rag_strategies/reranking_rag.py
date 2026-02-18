"""
Stratégie RAG avancée avec Cross-Encoder Reranking.
Améliore drastiquement la pertinence des documents récupérés.
"""

from typing import List, Dict
from src.rag_strategies.base import RAGStrategy
from src.reranker import Reranker
from src.search import _vectordb as collection


class RerankingRAG(RAGStrategy):
    """
    RAG avec reranking par Cross-Encoder.
    
    Pipeline:
    1. Récupération initiale (k * 2 documents)
    2. Reranking avec Cross-Encoder
    3. Sélection des top-k documents reranked
    4. Génération de la réponse
    """
    
    def __init__(self, llm=None, user_access_level: str = "public", rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialise le RAG avec reranking.
        
        Args:
            llm: Modèle de langage à utiliser
            user_access_level: Niveau d'accès de l'utilisateur
            rerank_model: Modèle de Cross-Encoder à utiliser
        """
        super().__init__(llm)
        self.user_access_level = user_access_level
        self.reranker = Reranker(model_name=rerank_model)
        self.collection = collection
        print(f"✅ RerankingRAG initialisé avec access_level={user_access_level}")
    
    def retrieve(self, query: str, k: int = 3, user_access_level: str = None) -> List[Dict]:
        """
        Récupère et reranke les documents pertinents.
        
        Args:
            query: Question de l'utilisateur
            k: Nombre final de documents à retourner
            user_access_level: Niveau d'accès (override)
        
        Returns:
            Liste des k documents les plus pertinents après reranking
        """
        access_level = user_access_level or self.user_access_level
        
        # Convertir le rôle en niveaux d'accès autorisés
        allowed_levels = self._get_allowed_levels(access_level)
        
        # Récupérer plus de documents pour le reranking (2x k)
        initial_k = k * 2
        
        print(f"🔍 Récupération initiale de {initial_k} documents (access: {allowed_levels})...")
        
        # Utiliser similarity_search avec filtre
        results = self.collection.similarity_search(
            query=query,
            k=initial_k,
            filter={"access_level": {"$in": allowed_levels}}
        )
        
        if not results:
            print("⚠️ Aucun document trouvé")
            return []
        
        # Préparer les documents pour le reranking
        documents = []
        for doc in results:
            documents.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        
        print(f"📊 Reranking de {len(documents)} documents...")
        # Reranker les documents
        reranked_docs = self.reranker.rerank(query, documents, top_k=k)
        
        # Extraire uniquement les documents (sans les scores)
        final_docs = [doc for doc, score in reranked_docs]
        
        print(f"✅ {len(final_docs)} documents reranked retournés")
        return final_docs
    
    def _get_allowed_levels(self, access_level: str) -> List[str]:
        """
        Convertit le niveau d'accès utilisateur en liste de niveaux autorisés.
        
        Args:
            access_level: Niveau d'accès utilisateur (public, internal, confidential)
        
        Returns:
            Liste des niveaux d'accès autorisés
        """
        access_hierarchy = {
            "public": ["public"],
            "internal": ["public", "internal"],
            "confidential": ["public", "internal", "confidential"]
        }
        return access_hierarchy.get(access_level, ["public"])
    
    def build_prompt(self, query, documents):
        """
        Construit le prompt pour le LLM avec les documents reranked.
        
        Args:
            query: Question de l'utilisateur
            documents: Documents récupérés et reranked
        
        Returns:
            Prompt formaté pour le LLM
        """
        context = "\n\n".join(doc.page_content if hasattr(doc, 'page_content') else doc.get('page_content', '') for doc in documents)

        return f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{query}
""".strip()


class HybridRerankingRAG(RAGStrategy):
    """
    RAG hybride avec BM25 et reranking par Cross-Encoder.
    
    Pipeline:
    1. Récupération vectorielle
    2. Récupération lexicale (BM25)
    3. Fusion des résultats
    4. Reranking avec Cross-Encoder
    5. Génération de la réponse
    """
    
    def __init__(self, llm=None, user_access_level: str = "public", rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialise le RAG hybride avec reranking.
        
        Args:
            llm: Modèle de langage à utiliser
            user_access_level: Niveau d'accès de l'utilisateur
            rerank_model: Modèle de Cross-Encoder à utiliser
        """
        super().__init__(llm)
        self.user_access_level = user_access_level
        self.reranker = Reranker(model_name=rerank_model)
        self.collection = collection
        
        # Importer BM25 pour la recherche lexicale
        try:
            from rank_bm25 import BM25Okapi
            self.BM25Okapi = BM25Okapi
            self.bm25_enabled = True
        except ImportError:
            print("⚠️ rank_bm25 non installé, recherche BM25 désactivée")
            self.bm25_enabled = False
        
        # Charger tous les documents pour BM25
        if self.bm25_enabled:
            self._init_bm25()
        
        print(f"✅ HybridRerankingRAG initialisé avec access_level={user_access_level}")
    
    def _init_bm25(self):
        """Initialise l'index BM25 avec tous les documents."""
        print("📚 Initialisation de l'index BM25...")
        
        # Accéder au client ChromaDB sous-jacent
        chroma_collection = self.collection._collection
        all_results = chroma_collection.get()
        
        if all_results and all_results["documents"]:
            self.all_documents = []
            self.all_metadatas = all_results["metadatas"]
            
            # Tokeniser les documents pour BM25
            tokenized_corpus = []
            for doc in all_results["documents"]:
                self.all_documents.append(doc)
                tokenized_corpus.append(doc.lower().split())
            
            self.bm25 = self.BM25Okapi(tokenized_corpus)
            print(f"✅ Index BM25 créé avec {len(self.all_documents)} documents")
        else:
            print("⚠️ Aucun document trouvé pour BM25")
            self.bm25_enabled = False
    
    def retrieve(self, query: str, k: int = 3, user_access_level: str = None) -> List[Dict]:
        """
        Récupère les documents avec recherche hybride + reranking.
        
        Args:
            query: Question de l'utilisateur
            k: Nombre final de documents à retourner
            user_access_level: Niveau d'accès (override)
        
        Returns:
            Liste des k documents les plus pertinents après reranking hybride
        """
        access_level = user_access_level or self.user_access_level
        allowed_levels = self._get_allowed_levels(access_level)
        
        # 1. Récupération vectorielle
        print(f"🔍 Récupération vectorielle (k={k*2})...")
        vector_results = self.collection.similarity_search(
            query=query,
            k=k * 2,
            filter={"access_level": {"$in": allowed_levels}}
        )
        
        vector_docs = []
        for doc in vector_results:
            vector_docs.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata,
                "source": "vector",
                "score": 0.5
            })
        
        # 2. Récupération BM25 (si activé)
        bm25_docs = []
        if self.bm25_enabled:
            print(f"📝 Récupération BM25 (k={k*2})...")
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # Obtenir les top k*2 documents BM25
            top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:k*2]
            
            for idx in top_indices:
                # Vérifier le niveau d'accès
                if self.all_metadatas[idx].get("access_level") in allowed_levels:
                    bm25_docs.append({
                        "page_content": self.all_documents[idx],
                        "metadata": self.all_metadatas[idx],
                        "source": "bm25",
                        "score": float(bm25_scores[idx])
                    })
        
        # 3. Fusion des résultats (dédupliquer)
        all_docs = vector_docs + bm25_docs
        unique_docs = {}
        for doc in all_docs:
            doc_id = doc["page_content"][:100]  # Clé unique basée sur le contenu
            if doc_id not in unique_docs:
                unique_docs[doc_id] = doc
        
        combined_docs = list(unique_docs.values())
        print(f"🔀 {len(combined_docs)} documents uniques après fusion")
        
        if not combined_docs:
            return []
        
        # 4. Reranking avec Cross-Encoder
        print(f"📊 Reranking de {len(combined_docs)} documents...")
        reranked_docs = self.reranker.rerank(query, combined_docs, top_k=k)
        
        # Extraire uniquement les documents
        final_docs = [doc for doc, score in reranked_docs]
        
        print(f"✅ {len(final_docs)} documents finaux retournés")
        return final_docs
    
    def _get_allowed_levels(self, access_level: str) -> List[str]:
        """Convertit le niveau d'accès en liste de niveaux autorisés."""
        access_hierarchy = {
            "public": ["public"],
            "internal": ["public", "internal"],
            "confidential": ["public", "internal", "confidential"]
        }
        return access_hierarchy.get(access_level, ["public"])
    
    def build_prompt(self, query, documents):
        """
        Construit le prompt pour le LLM avec les documents reranked.
        
        Args:
            query: Question de l'utilisateur
            documents: Documents récupérés et reranked
        
        Returns:
            Prompt formaté pour le LLM
        """
        context = "\n\n".join(
            f"- {doc.page_content if hasattr(doc, 'page_content') else doc.get('page_content', '')}"
            for doc in documents
        )

        return f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{query}
""".strip()
