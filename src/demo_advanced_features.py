"""
Script de démonstration des nouvelles fonctionnalités:
1. Reranking avec Cross-Encoder
2. Métriques d'évaluation qualitative (MRR, NDCG, similarité sémantique)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reranker import Reranker
from src.evaluation_metrics import RAGEvaluator
from src.rag_strategies.reranking_rag import RerankingRAG, HybridRerankingRAG
from src.rag_strategies.simple_rag import SimpleRAG
from src.search import _vectordb as collection  # Utiliser la collection ChromaDB existante
from src.llms.gemini_llm import GeminiLLM
import json


def demo_reranking():
    """Démontre l'impact du reranking sur la qualité des résultats."""
    print("\n" + "="*80)
    print("🎯 DÉMONSTRATION: Impact du Reranking")
    print("="*80 + "\n")
    
    # Requête de test
    query = "Quel est le montant du contrat de l'hôpital San Juan de Dios?"
    print(f"\n❓ Question: {query}\n")
    
    # 1. RAG simple (sans reranking)
    print("1️⃣ RAG SIMPLE (sans reranking)")
    print("-" * 80)
    simple_rag = SimpleRAG()
    simple_docs = simple_rag.retrieve(query, k=5, user_access_level="internal")
    
    print(f"Nombre de documents: {len(simple_docs)}")
    for i, doc in enumerate(simple_docs, 1):
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"  {i}. {preview}...")
    
    # 2. RAG avec reranking
    print("\n2️⃣ RAG AVEC RERANKING")
    print("-" * 80)
    reranking_rag = RerankingRAG(user_access_level="internal")
    reranked_docs = reranking_rag.retrieve(query, k=5, user_access_level="internal")
    
    print(f"Nombre de documents: {len(reranked_docs)}")
    for i, doc in enumerate(reranked_docs, 1):
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"  {i}. {preview}...")
    
    print("\n💡 Comparaison:")
    print(f"   - Les documents sont réordonnés par pertinence")
    print(f"   - Le reranking utilise un Cross-Encoder pour une meilleure évaluation")


def demo_evaluation_metrics():
    """Démontre l'utilisation des métriques d'évaluation."""
    print("\n" + "="*80)
    print("📊 DÉMONSTRATION: Métriques d'Évaluation Qualitative")
    print("="*80 + "\n")
    
    # Initialiser l'évaluateur
    evaluator = RAGEvaluator()
    
    # Exemple de réponses
    ground_truth = "Le montant total du contrat est de 468 millions de pesos."
    generated_answer_good = "Le contrat a un montant de 468000000 pesos (468 millions)."
    generated_answer_bad = "Le contrat concerne l'hôpital San Juan de Dios."
    
    print("🎯 Ground Truth:")
    print(f"   {ground_truth}\n")
    
    # Évaluer bonne réponse
    print("✅ BONNE RÉPONSE:")
    print(f"   {generated_answer_good}")
    
    metrics_good = evaluator.evaluate_generation(generated_answer_good, ground_truth)
    print("\n   Métriques:")
    print(f"   - Similarité sémantique: {metrics_good['semantic_similarity']:.3f}")
    print(f"   - Exact match: {metrics_good['exact_match']}")
    print(f"   - F1 score: {metrics_good['f1_score']:.3f}")
    
    # Évaluer mauvaise réponse
    print("\n❌ MAUVAISE RÉPONSE:")
    print(f"   {generated_answer_bad}")
    
    metrics_bad = evaluator.evaluate_generation(generated_answer_bad, ground_truth)
    print("\n   Métriques:")
    print(f"   - Similarité sémantique: {metrics_bad['semantic_similarity']:.3f}")
    print(f"   - Exact match: {metrics_bad['exact_match']}")
    print(f"   - F1 score: {metrics_bad['f1_score']:.3f}")
    
    # Démonstration MRR et NDCG
    print("\n" + "-"*80)
    print("📈 Métriques de Retrieval (MRR, NDCG@k)")
    print("-"*80 + "\n")
    
    # Simuler des documents récupérés
    retrieved_docs = [
        {"metadata": {"source": "doc1"}},
        {"metadata": {"source": "doc2"}},
        {"metadata": {"source": "doc3"}},
    ]
    
    relevant_doc_ids = ["doc2", "doc1"]  # doc2 est le plus pertinent
    relevance_scores = [2, 3, 0]  # doc2 a le score le plus élevé
    
    # Calculer MRR
    mrr = evaluator.calculate_mrr(retrieved_docs, relevant_doc_ids)
    print(f"MRR (Mean Reciprocal Rank): {mrr:.3f}")
    print(f"   → Le premier document pertinent est en position {int(1/mrr) if mrr > 0 else 'N/A'}")
    
    # Calculer NDCG@3
    ndcg = evaluator.calculate_ndcg_at_k(retrieved_docs, relevance_scores, k=3)
    print(f"\nNDCG@3 (Normalized Discounted Cumulative Gain): {ndcg:.3f}")
    print(f"   → Qualité du classement: {'Excellent' if ndcg > 0.8 else 'Bon' if ndcg > 0.6 else 'Moyen' if ndcg > 0.4 else 'Faible'}")
    
    # Calculer Precision et Recall
    precision = evaluator.calculate_precision_at_k(retrieved_docs, relevant_doc_ids, k=3)
    recall = evaluator.calculate_recall_at_k(retrieved_docs, relevant_doc_ids, k=3)
    
    print(f"\nPrecision@3: {precision:.3f}")
    print(f"   → {int(precision * 3)} documents pertinents sur 3 récupérés")
    
    print(f"\nRecall@3: {recall:.3f}")
    print(f"   → {int(recall * len(relevant_doc_ids))} documents pertinents trouvés sur {len(relevant_doc_ids)} au total")


def demo_full_pipeline():
    """Démontre l'évaluation complète d'un pipeline RAG."""
    print("\n" + "="*80)
    print("🔄 DÉMONSTRATION: Évaluation Complète du Pipeline RAG")
    print("="*80 + "\n")
    
    # Charger une question de test
    with open("data/test_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    test_question = questions[2]  # Question sur l'hôpital
    
    print(f"❓ Question: {test_question['question']}")
    print(f"🎯 Réponse attendue: {test_question['expected_answer']}\n")
    
    # Initialiser le RAG avec reranking
    print("🚀 Exécution du pipeline RAG avec reranking...")
    llm = GeminiLLM()
    reranking_rag = RerankingRAG(llm=llm, user_access_level=test_question["access_level"])
    
    # Récupérer les documents
    docs = reranking_rag.retrieve(test_question["question"], k=3)
    
    # Générer la réponse
    response = reranking_rag.answer(test_question["question"], user_access_level=test_question["access_level"])
    
    print(f"\n💬 Réponse générée:\n{response}\n")
    
    # Évaluer
    print("📊 Évaluation de la qualité...")
    evaluator = RAGEvaluator()
    
    metrics = evaluator.evaluate_full_pipeline(
        retrieved_docs=docs,
        generated_answer=response,
        ground_truth_answer=test_question["expected_answer"],
        relevant_doc_ids=test_question.get("relevant_doc_ids", []),
        relevance_scores=test_question.get("relevance_scores", []),
        k=3
    )
    
    print("\n📈 RÉSULTATS D'ÉVALUATION:")
    print("-" * 80)
    
    print("\n🔍 Métriques de Retrieval:")
    for key, value in metrics.items():
        if key.startswith("retrieval_"):
            metric_name = key.replace("retrieval_", "")
            if isinstance(value, bool):
                print(f"   - {metric_name}: {value}")
            else:
                print(f"   - {metric_name}: {value:.3f}")
    
    print("\n✍️ Métriques de Generation:")
    for key, value in metrics.items():
        if key.startswith("generation_"):
            metric_name = key.replace("generation_", "")
            if isinstance(value, bool):
                print(f"   - {metric_name}: {value}")
            elif isinstance(value, (int, float)) and metric_name not in ["answer_length", "ground_truth_length"]:
                print(f"   - {metric_name}: {value:.3f}")
            else:
                print(f"   - {metric_name}: {value}")


def main():
    """Exécute toutes les démonstrations."""
    print("\n" + "🎉"*40)
    print("DÉMONSTRATION DES NOUVELLES FONCTIONNALITÉS")
    print("🎉"*40)
    
    try:
        # Démo 1: Reranking
        demo_reranking()
        
        input("\n\nAppuyez sur Entrée pour continuer vers la démo des métriques...")
        
        # Démo 2: Métriques d'évaluation
        demo_evaluation_metrics()
        
        input("\n\nAppuyez sur Entrée pour continuer vers l'évaluation complète...")
        
        # Démo 3: Pipeline complet
        demo_full_pipeline()
        
        print("\n" + "="*80)
        print("✅ DÉMONSTRATION TERMINÉE")
        print("="*80 + "\n")
        
        print("📝 Résumé des améliorations:")
        print("   1. ⭐ Reranking avec Cross-Encoder → Meilleure pertinence des documents")
        print("   2. ⭐ MRR, NDCG@k → Mesure de la qualité du retrieval")
        print("   3. ⭐ Similarité sémantique, F1 → Mesure de la qualité de génération")
        print("   4. ⭐ Évaluation complète du pipeline RAG end-to-end")
        
    except KeyboardInterrupt:
        print("\n\n❌ Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
