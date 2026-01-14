from rag_strategies.simple_rag import SimpleRAG
from rag_strategies.secure_rag import SecureRAG
from rag_strategies.hybrid_rag import HybridRAG
from rag_strategies.modular_rag import ModularRAG

from llms.ollama_llm import OllamaLLM
from llms.openai_llm import OpenAILLM
from llms.gemini_llm import GeminiLLM


def get_rag_strategy(name: str):
    if name == "simple":
        return SimpleRAG()
    if name == "secure":
        return SecureRAG()
    if name == "hybrid":
        return HybridRAG()
    if name == "modular":
        return ModularRAG()
    raise ValueError(f"Unknown RAG strategy: {name}")


def get_llm(name: str):
    if name == "ollama":
        return OllamaLLM()
    if name == "openai":
        return OpenAILLM()
    if name == "gemini":
        return GeminiLLM()
    raise ValueError(f"Unknown LLM: {name}")
