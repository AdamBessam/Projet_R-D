from rag_strategies.simple_rag import SimpleRAG
from rag_strategies.secure_rag import SecureRAG
from rag_strategies.hybrid_rag import HybridRAG
from rag_strategies.modular_rag import ModularRAG

from llms.mistral import MistralLLM
from llms.qwen import QwenLLM
from llms.gemini_llm import GeminiLLM
from llms.llama import LlamaLLM

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
    if name == "mistral":
        return MistralLLM()
    if name == "qwen":
        return QwenLLM()
    if name == "gemini":
        return GeminiLLM()
    if name == "llama":
        return LlamaLLM()
    raise ValueError(f"Unknown LLM: {name}")
