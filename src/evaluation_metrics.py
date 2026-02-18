"""
Métriques d'évaluation qualitative pour les systèmes RAG.
Inclut MRR, NDCG@k, similarité sémantique, et autres métriques de pertinence.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re


class RAGEvaluator:
    """
    Évaluateur pour mesurer la qualité des réponses RAG.
    """
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialise l'évaluateur.
        
        Args:
            embedding_model: Modèle pour calculer la similarité sémantique
        """
        print(f"📊 Chargement du modèle d'embedding pour l'évaluation: {embedding_model}...")
        self.embedder = SentenceTransformer(embedding_model)
        print("✅ Modèle d'évaluation chargé")
    
    def calculate_mrr(self, retrieved_docs: List[dict], relevant_doc_ids: List[str]) -> float:
        """
        Calcule le Mean Reciprocal Rank (MRR).
        
        MRR mesure à quelle position apparaît le premier document pertinent.
        Score parfait = 1.0 (document pertinent en position 1)
        
        Args:
            retrieved_docs: Documents récupérés par le système
            relevant_doc_ids: IDs des documents vraiment pertinents
        
        Returns:
            Score MRR entre 0 et 1
        """
        for rank, doc in enumerate(retrieved_docs, start=1):
            doc_id = doc.get("metadata", {}).get("source", "")
            if doc_id in relevant_doc_ids:
                return 1.0 / rank
        return 0.0
    
    def calculate_ndcg_at_k(
        self, 
        retrieved_docs: List[dict], 
        relevance_scores: List[float],
        k: int = 5
    ) -> float:
        """
        Calcule le Normalized Discounted Cumulative Gain à la position k.
        
        NDCG@k mesure la qualité du classement en tenant compte de la position.
        Score parfait = 1.0
        
        Args:
            retrieved_docs: Documents récupérés (top k)
            relevance_scores: Scores de pertinence pour chaque document (0-3 typiquement)
            k: Nombre de documents à considérer
        
        Returns:
            Score NDCG@k entre 0 et 1
        """
        if not retrieved_docs or not relevance_scores:
            return 0.0
        
        # Limiter à k documents
        relevance_scores = relevance_scores[:k]
        
        # DCG: somme des (pertinence / log2(position+1))
        dcg = sum(
            (2**rel - 1) / np.log2(i + 2)  # i+2 car index commence à 0
            for i, rel in enumerate(relevance_scores)
        )
        
        # IDCG: DCG si les documents étaient parfaitement classés
        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = sum(
            (2**rel - 1) / np.log2(i + 2)
            for i, rel in enumerate(ideal_scores)
        )
        
        # NDCG = DCG / IDCG
        return dcg / idcg if idcg > 0 else 0.0
    
    def calculate_precision_at_k(
        self,
        retrieved_docs: List[dict],
        relevant_doc_ids: List[str],
        k: int = 5
    ) -> float:
        """
        Calcule la précision à la position k (Precision@k).
        
        Precision@k = (nombre de docs pertinents dans top-k) / k
        
        Args:
            retrieved_docs: Documents récupérés
            relevant_doc_ids: IDs des documents pertinents
            k: Nombre de documents à considérer
        
        Returns:
            Score de précision entre 0 et 1
        """
        if not retrieved_docs:
            return 0.0
        
        top_k_docs = retrieved_docs[:k]
        relevant_count = sum(
            1 for doc in top_k_docs
            if doc.get("metadata", {}).get("source", "") in relevant_doc_ids
        )
        
        return relevant_count / k
    
    def calculate_recall_at_k(
        self,
        retrieved_docs: List[dict],
        relevant_doc_ids: List[str],
        k: int = 5
    ) -> float:
        """
        Calcule le recall à la position k (Recall@k).
        
        Recall@k = (nombre de docs pertinents dans top-k) / (total docs pertinents)
        
        Args:
            retrieved_docs: Documents récupérés
            relevant_doc_ids: IDs des documents pertinents
            k: Nombre de documents à considérer
        
        Returns:
            Score de recall entre 0 et 1
        """
        if not relevant_doc_ids:
            return 0.0
        
        top_k_docs = retrieved_docs[:k]
        relevant_count = sum(
            1 for doc in top_k_docs
            if doc.get("metadata", {}).get("source", "") in relevant_doc_ids
        )
        
        return relevant_count / len(relevant_doc_ids)
    
    def calculate_semantic_similarity(
        self,
        generated_answer: str,
        ground_truth_answer: str
    ) -> float:
        """
        Calcule la similarité sémantique entre la réponse générée et la ground truth.
        
        Utilise les embeddings pour comparer le sens, pas juste les mots.
        
        Args:
            generated_answer: Réponse générée par le système
            ground_truth_answer: Réponse attendue
        
        Returns:
            Score de similarité cosinus entre 0 et 1
        """
        if not generated_answer or not ground_truth_answer:
            return 0.0
        
        # Générer les embeddings
        embeddings = self.embedder.encode([generated_answer, ground_truth_answer])
        
        # Calculer la similarité cosinus
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return float(similarity)
    
    def calculate_exact_match(
        self,
        generated_answer: str,
        ground_truth_answer: str,
        case_sensitive: bool = False
    ) -> bool:
        """
        Vérifie si la réponse générée contient exactement la ground truth.
        
        Args:
            generated_answer: Réponse générée
            ground_truth_answer: Réponse attendue
            case_sensitive: Si True, respecte la casse
        
        Returns:
            True si correspondance exacte, False sinon
        """
        if not case_sensitive:
            generated_answer = generated_answer.lower()
            ground_truth_answer = ground_truth_answer.lower()
        
        # Nettoyer les espaces
        generated_answer = " ".join(generated_answer.split())
        ground_truth_answer = " ".join(ground_truth_answer.split())
        
        return ground_truth_answer in generated_answer
    
    def calculate_f1_score(
        self,
        generated_answer: str,
        ground_truth_answer: str
    ) -> float:
        """
        Calcule le F1-score token-level entre la réponse générée et la ground truth.
        
        Args:
            generated_answer: Réponse générée
            ground_truth_answer: Réponse attendue
        
        Returns:
            F1-score entre 0 et 1
        """
        # Tokeniser (simple split sur les mots)
        gen_tokens = set(re.findall(r'\w+', generated_answer.lower()))
        truth_tokens = set(re.findall(r'\w+', ground_truth_answer.lower()))
        
        if not truth_tokens:
            return 0.0
        
        # Calculer l'intersection
        common_tokens = gen_tokens & truth_tokens
        
        if not common_tokens:
            return 0.0
        
        # Precision = tokens communs / tokens générés
        precision = len(common_tokens) / len(gen_tokens) if gen_tokens else 0
        
        # Recall = tokens communs / tokens ground truth
        recall = len(common_tokens) / len(truth_tokens)
        
        # F1 = moyenne harmonique
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return f1
    
    def evaluate_retrieval(
        self,
        retrieved_docs: List[dict],
        relevant_doc_ids: Optional[List[str]] = None,
        relevance_scores: Optional[List[float]] = None,
        k: int = 5
    ) -> Dict[str, float]:
        """
        Évalue la qualité de la récupération de documents.
        
        Args:
            retrieved_docs: Documents récupérés par le système
            relevant_doc_ids: IDs des documents pertinents (pour MRR, P@k, R@k)
            relevance_scores: Scores de pertinence 0-3 (pour NDCG@k)
            k: Nombre de documents à considérer
        
        Returns:
            Dictionnaire avec toutes les métriques
        """
        metrics = {}
        
        if relevant_doc_ids:
            metrics["mrr"] = self.calculate_mrr(retrieved_docs, relevant_doc_ids)
            metrics[f"precision@{k}"] = self.calculate_precision_at_k(retrieved_docs, relevant_doc_ids, k)
            metrics[f"recall@{k}"] = self.calculate_recall_at_k(retrieved_docs, relevant_doc_ids, k)
        
        if relevance_scores:
            metrics[f"ndcg@{k}"] = self.calculate_ndcg_at_k(retrieved_docs, relevance_scores, k)
        
        return metrics
    
    def evaluate_generation(
        self,
        generated_answer: str,
        ground_truth_answer: str
    ) -> Dict[str, Any]:
        """
        Évalue la qualité de la réponse générée.
        
        Args:
            generated_answer: Réponse générée par le LLM
            ground_truth_answer: Réponse attendue
        
        Returns:
            Dictionnaire avec toutes les métriques de génération
        """
        return {
            "semantic_similarity": self.calculate_semantic_similarity(generated_answer, ground_truth_answer),
            "exact_match": self.calculate_exact_match(generated_answer, ground_truth_answer),
            "f1_score": self.calculate_f1_score(generated_answer, ground_truth_answer),
            "answer_length": len(generated_answer.split()),
            "ground_truth_length": len(ground_truth_answer.split())
        }
    
    def evaluate_full_pipeline(
        self,
        retrieved_docs: List[dict],
        generated_answer: str,
        ground_truth_answer: str,
        relevant_doc_ids: Optional[List[str]] = None,
        relevance_scores: Optional[List[float]] = None,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Évalue le pipeline RAG complet (retrieval + generation).
        
        Args:
            retrieved_docs: Documents récupérés
            generated_answer: Réponse générée
            ground_truth_answer: Réponse attendue
            relevant_doc_ids: IDs des documents pertinents
            relevance_scores: Scores de pertinence
            k: Nombre de documents à considérer
        
        Returns:
            Dictionnaire avec toutes les métriques
        """
        metrics = {}
        
        # Métriques de retrieval
        retrieval_metrics = self.evaluate_retrieval(
            retrieved_docs, relevant_doc_ids, relevance_scores, k
        )
        metrics.update({f"retrieval_{key}": value for key, value in retrieval_metrics.items()})
        
        # Métriques de generation
        generation_metrics = self.evaluate_generation(generated_answer, ground_truth_answer)
        metrics.update({f"generation_{key}": value for key, value in generation_metrics.items()})
        
        return metrics


def create_evaluator(embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2") -> RAGEvaluator:
    """
    Crée une instance de RAGEvaluator.
    
    Args:
        embedding_model: Modèle à utiliser pour les embeddings
    
    Returns:
        Instance de RAGEvaluator
    """
    return RAGEvaluator(embedding_model)
