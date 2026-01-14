import requests
from .base import LLM

class OllamaLLM(LLM):

    def __init__(self, model="mistral"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=900
        )
        response.raise_for_status()
        return response.json()["response"]
