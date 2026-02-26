import requests
from .base import LLM

class QwenLLM(LLM):

    def __init__(self, model="qwen3:8b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        try:
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
            try:
                return response.json().get("response", response.text)
            except ValueError:
                return response.text
        except requests.exceptions.HTTPError as e:
            body = getattr(e.response, "text", None) if hasattr(e, "response") else None
            raise RuntimeError(
                f"Ollama API HTTP error {getattr(e.response, 'status_code', '')}: {body}"
            ) from e
