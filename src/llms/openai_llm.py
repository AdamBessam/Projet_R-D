import os
from openai import OpenAI
from .base import LLM

class OpenAILLM(LLM):

    def __init__(self, model="gpt-4o-mini"):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
