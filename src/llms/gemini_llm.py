import os
from google import genai
from .base import LLM

class GeminiLLM(LLM):

    def __init__(self, model="gemini-2.5-flash"):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text
