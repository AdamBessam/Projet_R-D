from abc import ABC, abstractmethod

class RAGStrategy(ABC):
    
    def __init__(self, llm=None):
        self.llm = llm

    @abstractmethod
    def retrieve(self, query: str, user_access_level: str = "public"):
        pass

    @abstractmethod
    def build_prompt(self, query: str, documents):
        pass
    
    def answer(self, query: str, user_access_level: str = "public") -> str:
        """Génère une réponse complète à partir de la question"""
        docs = self.retrieve(query, user_access_level)
        prompt = self.build_prompt(query, docs)
        if self.llm:
            return self.llm.generate(prompt)
        return "LLM not configured"
