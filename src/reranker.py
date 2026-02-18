"""
Module de reranking avec Cross-Encoder pour améliorer la pertinence des documents.
Le Cross-Encoder évalue la pertinence entre la requête et chaque document.
"""

from typing import List, Tuple
from sentence_transformers import CrossEncoder
import numpy as np


class Reranker:
    """
    Reranker utilisant un Cross-Encoder pour améliorer la pertinence des documents.
    
    Le Cross-Encoder encode simultanément la requête et le document,
    ce qui donne une meilleure évaluation de la pertinence qu'un bi-encoder classique.
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialise le reranker.
        
        Args:
            model_name: Nom du modèle Cross-Encoder à utiliser
                       Options recommandées:
                       - "cross-encoder/ms-marco-MiniLM-L-6-v2" (rapide, bon)
                       - "cross-encoder/ms-marco-MiniLM-L-12-v2" (plus lent, meilleur)
                       - "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1" (multilingue)
        """
        print(f"📊 Chargement du Cross-Encoder: {model_name}...")
        self.model = CrossEncoder(model_name)
        print("✅ Cross-Encoder chargé avec succès")
    
    def rerank(
        self, 
        query: str, 
        documents: List[dict], 
        top_k: int = None
    ) -> List[Tuple[dict, float]]:
        """
        Rerank les documents selon leur pertinence avec la requête.
        
        Args:
            query: Question de l'utilisateur
            documents: Liste de documents ChromaDB (avec 'page_content' et 'metadata')
            top_k: Nombre de documents à retourner (None = tous)
        
        Returns:
            Liste de tuples (document, score) triée par score décroissant
        """
        if not documents:
            return []
        
        # Préparer les paires (query, document) pour le Cross-Encoder
        pairs = []
        for doc in documents:
            # Extraire le texte du document
            text = doc.get("page_content", "") if isinstance(doc, dict) else str(doc)
            pairs.append([query, text])
        
        # Calculer les scores de pertinence
        scores = self.model.predict(pairs)
        
        # Créer des tuples (document, score)
        ranked_docs = list(zip(documents, scores))
        
        # Trier par score décroissant
        ranked_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Limiter au top_k si spécifié
        if top_k is not None:
            ranked_docs = ranked_docs[:top_k]
        
        return ranked_docs
    
    def get_scores(self, query: str, documents: List[dict]) -> np.ndarray:
        """
        Retourne uniquement les scores de pertinence.
        
        Args:
            query: Question de l'utilisateur
            documents: Liste de documents
        
        Returns:
            Array numpy des scores
        """
        if not documents:
            return np.array([])
        
        pairs = [[query, doc.get("page_content", "")] for doc in documents]
        return self.model.predict(pairs)


class HybridReranker(Reranker):
    """
    Reranker hybride combinant le score du Cross-Encoder avec le score original.
    """
    
    def rerank_with_fusion(
        self,
        query: str,
        documents: List[dict],
        original_scores: List[float],
        alpha: float = 0.7,
        top_k: int = None
    ) -> List[Tuple[dict, float]]:
        """
        Combine les scores originaux (similarité vectorielle) avec les scores du Cross-Encoder.
        
        Args:
            query: Question de l'utilisateur
            documents: Liste de documents
            original_scores: Scores de similarité vectorielle originaux
            alpha: Poids du Cross-Encoder (0-1). 0.7 = 70% Cross-Encoder, 30% score original
            top_k: Nombre de documents à retourner
        
        Returns:
            Liste de tuples (document, score_fusionné) triée
        """
        if not documents:
            return []
        
        # Obtenir les scores du Cross-Encoder
        ce_scores = self.get_scores(query, documents)
        
        # Normaliser les scores entre 0 et 1
        ce_scores_norm = (ce_scores - ce_scores.min()) / (ce_scores.max() - ce_scores.min() + 1e-10)
        orig_scores_norm = np.array(original_scores)
        orig_scores_norm = (orig_scores_norm - orig_scores_norm.min()) / (orig_scores_norm.max() - orig_scores_norm.min() + 1e-10)
        
        # Fusion des scores
        fused_scores = alpha * ce_scores_norm + (1 - alpha) * orig_scores_norm
        
        # Créer des tuples (document, score)
        ranked_docs = list(zip(documents, fused_scores))
        
        # Trier par score décroissant
        ranked_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Limiter au top_k si spécifié
        if top_k is not None:
            ranked_docs = ranked_docs[:top_k]
        
        return ranked_docs


# Fonction utilitaire pour faciliter l'utilisation
def create_reranker(model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> Reranker:
    """
    Crée une instance de Reranker.
    
    Args:
        model_name: Nom du modèle à utiliser
    
    Returns:
        Instance de Reranker
    """
    return Reranker(model_name)
