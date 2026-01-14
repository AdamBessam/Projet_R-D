from abc import ABC, abstractmethod

class RAGStrategy(ABC):

    @abstractmethod
    def retrieve(self, query: str, user_access_level: str):
        pass

    @abstractmethod
    def build_prompt(self, query: str, documents):
        pass
