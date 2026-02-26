"""
Module de benchmarking pour comparer les performances des LLMs et stratégies RAG
"""
import time
import json
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path
import sys

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag_strategies.simple_rag import SimpleRAG
from src.rag_strategies.secure_rag import SecureRAG
from src.rag_strategies.hybrid_rag import HybridRAG
from src.rag_strategies.modular_rag import ModularRAG
from src.llms.openai_llm import OpenAILLM
from src.llms.mistral import MistralLLM
from src.llms.gemini_llm import GeminiLLM


class RAGBenchmark:
    """Classe pour effectuer des benchmarks sur différents LLMs et stratégies RAG"""
    
    def __init__(self, test_questions_path: str = "data/test_questions.json"):
        """
        Initialise le benchmark
        
        Args:
            test_questions_path: Chemin vers le fichier JSON des questions de test
        """
        self.test_questions_path = test_questions_path
        self.questions = self._load_questions()
        self.results = []
        
        # Mapping des LLMs
        self.llms = {
            "openai": OpenAILLM,
            "ollama": MistralLLM,
            "gemini": GeminiLLM
        }
        
        # Mapping des stratégies
        self.strategies = {
            "simple": SimpleRAG,
            "secure": SecureRAG,
            "hybrid": HybridRAG,
            "modular": ModularRAG
        }
    
    def _load_questions(self) -> List[Dict]:
        """Charge les questions de test depuis le fichier JSON"""
        try:
            with open(self.test_questions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Fichier {self.test_questions_path} non trouvé")
            return []
    
    def run_single_test(
        self, 
        question: Dict, 
        llm_name: str, 
        strategy_name: str,
        user_access_level: str = "internal"
    ) -> Dict:
        """
        Exécute un test unique avec une question, un LLM et une stratégie
        
        Args:
            question: Dictionnaire contenant la question et métadonnées
            llm_name: Nom du LLM à utiliser
            strategy_name: Nom de la stratégie RAG à utiliser
            user_access_level: Niveau d'accès de l'utilisateur pour SecureRAG
            
        Returns:
            Dictionnaire avec les résultats du test
        """
        try:
            # Initialiser le LLM
            llm_class = self.llms[llm_name]
            llm = llm_class()
            
            # Initialiser la stratégie RAG
            strategy_class = self.strategies[strategy_name]
            if strategy_name == "secure":
                rag = strategy_class(llm=llm, user_access_level=user_access_level)
            else:
                rag = strategy_class(llm=llm)
            
            # Mesurer le temps total
            start_total = time.time()
            
            # Déterminer le niveau d'accès pour ce test
            test_access_level = question.get("access_level", user_access_level)
            
            # Récupération des documents
            retrieval_start = time.time()
            docs = rag.retrieve(question["question"], test_access_level)
            retrieval_time = time.time() - retrieval_start
            num_docs = len(docs) if docs else 0
            
            # Génération de la réponse
            llm_start = time.time()
            answer = rag.answer(question["question"], test_access_level)
            llm_time = time.time() - llm_start
            
            total_time = time.time() - start_total
            
            # Estimation des tokens (approximation)
            tokens_used = self._estimate_tokens(question["question"], answer, docs)
            
            return {
                "question_id": question["id"],
                "question": question["question"],
                "category": question.get("category", "unknown"),
                "difficulty": question.get("difficulty", "unknown"),
                "llm": llm_name,
                "strategy": strategy_name,
                "retrieval_time": round(retrieval_time, 3),
                "llm_time": round(llm_time, 3),
                "total_time": round(total_time, 3),
                "num_documents": num_docs,
                "answer": answer,
                "answer_length": len(answer) if answer else 0,
                "tokens_estimated": tokens_used,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "question_id": question.get("id", -1),
                "question": question.get("question", ""),
                "category": question.get("category", "unknown"),
                "difficulty": question.get("difficulty", "unknown"),
                "llm": llm_name,
                "strategy": strategy_name,
                "retrieval_time": 0,
                "llm_time": 0,
                "total_time": 0,
                "num_documents": 0,
                "answer": "",
                "answer_length": 0,
                "tokens_estimated": 0,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error_message": str(e)
            }
    
    def _estimate_tokens(self, question: str, answer: str, docs: List) -> int:
        """
        Estime le nombre de tokens utilisés (approximation)
        
        Args:
            question: Question posée
            answer: Réponse générée
            docs: Documents récupérés
            
        Returns:
            Estimation du nombre de tokens
        """
        # Approximation: 1 token ≈ 4 caractères
        question_tokens = len(question) // 4
        answer_tokens = len(answer) // 4 if answer else 0
        
        # Tokens du contexte (documents)
        context_tokens = 0
        if docs:
            for doc in docs:
                if hasattr(doc, 'page_content'):
                    context_tokens += len(doc.page_content) // 4
                elif isinstance(doc, str):
                    context_tokens += len(doc) // 4
        
        return question_tokens + answer_tokens + context_tokens
    
    def run_full_benchmark(
        self,
        llms_to_test: Optional[List[str]] = None,
        strategies_to_test: Optional[List[str]] = None,
        questions_to_test: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Exécute un benchmark complet sur toutes les combinaisons
        
        Args:
            llms_to_test: Liste des LLMs à tester (tous par défaut)
            strategies_to_test: Liste des stratégies à tester (toutes par défaut)
            questions_to_test: Liste des IDs de questions à tester (toutes par défaut)
            
        Returns:
            DataFrame avec tous les résultats
        """
        llms_to_test = llms_to_test or list(self.llms.keys())
        strategies_to_test = strategies_to_test or list(self.strategies.keys())
        
        # Filtrer les questions si nécessaire
        questions = self.questions
        if questions_to_test:
            questions = [q for q in questions if q["id"] in questions_to_test]
        
        total_tests = len(llms_to_test) * len(strategies_to_test) * len(questions)
        current_test = 0
        
        print(f"🚀 Démarrage du benchmark: {total_tests} tests à exécuter")
        print(f"LLMs: {', '.join(llms_to_test)}")
        print(f"Stratégies: {', '.join(strategies_to_test)}")
        print(f"Questions: {len(questions)}")
        print("-" * 60)
        
        for question in questions:
            for llm in llms_to_test:
                for strategy in strategies_to_test:
                    current_test += 1
                    print(f"[{current_test}/{total_tests}] Testing {llm} + {strategy} - Q{question['id']}")
                    
                    result = self.run_single_test(
                        question=question,
                        llm_name=llm,
                        strategy_name=strategy,
                        user_access_level=question.get("access_level", "internal")
                    )
                    
                    self.results.append(result)
                    
                    # Attendre entre les tests si on utilise Gemini pour éviter les quotas
                    if llm == "gemini" and current_test < total_tests:
                        print("⏳ Pause de 15 secondes pour respecter les quotas Gemini...")
                        time.sleep(15)
        
        print(f"✅ Benchmark terminé: {len(self.results)} résultats")
        return pd.DataFrame(self.results)
    
    def save_results(self, filepath: str = "reports/benchmark_results.csv"):
        """Sauvegarde les résultats dans un fichier CSV"""
        if not self.results:
            print("Aucun résultat à sauvegarder")
            return
        
        df = pd.DataFrame(self.results)
        
        # Créer le dossier si nécessaire
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"💾 Résultats sauvegardés dans {filepath}")
    
    def save_results_json(self, filepath: str = "reports/benchmark_results.json"):
        """Sauvegarde les résultats dans un fichier JSON"""
        if not self.results:
            print("Aucun résultat à sauvegarder")
            return
        
        # Créer le dossier si nécessaire
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés dans {filepath}")
    
    def get_summary_stats(self) -> pd.DataFrame:
        """Retourne un résumé statistique des résultats"""
        if not self.results:
            print("Aucun résultat disponible")
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        
        # Grouper par LLM et stratégie
        summary = df.groupby(['llm', 'strategy']).agg({
            'total_time': ['mean', 'median', 'std'],
            'retrieval_time': 'mean',
            'llm_time': 'mean',
            'num_documents': 'mean',
            'tokens_estimated': 'mean',
            'answer_length': 'mean',
            'status': lambda x: (x == 'success').sum()
        }).round(3)
        
        summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
        summary = summary.rename(columns={'status_<lambda>': 'success_count'})
        
        return summary


if __name__ == "__main__":
    # Exemple d'utilisation
    benchmark = RAGBenchmark()
    
    # Tester seulement quelques combinaisons avec Gemini (gratuit et déjà configuré)
    results_df = benchmark.run_full_benchmark(
        llms_to_test=["gemini"],  # Utiliser Gemini qui est déjà configuré
        strategies_to_test=["simple", "secure"],
        questions_to_test=[1, 2, 3]  # Quelques questions seulement
    )
    
    # Sauvegarder les résultats
    benchmark.save_results()
    benchmark.save_results_json()
    
    # Afficher le résumé
    print("\n📊 Résumé des performances:")
    print(benchmark.get_summary_stats())
