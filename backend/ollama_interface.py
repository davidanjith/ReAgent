import requests
from typing import Dict, List, Optional
import json

class OllamaInterface:
    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    def _create_prompt(self, question: str, context: str) -> str:
        """Create a prompt for the LLM with context."""
        return f"""You are a helpful research assistant. Use the following context to answer the question.
If you cannot answer the question based on the context, say so.

Context:
{context}

Question: {question}

Answer:"""

    async def generate_response(
        self,
        question: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """Generate a response from Ollama."""
        prompt = self._create_prompt(question, context)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "response": None
            }

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embeddings using Ollama's embedding endpoint."""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                }
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except requests.exceptions.RequestException:
            return None

    def format_response(self, response: Dict) -> Dict:
        """Format the response from Ollama."""
        if "error" in response:
            return {
                "success": False,
                "error": response["error"],
                "answer": None
            }
        
        return {
            "success": True,
            "error": None,
            "answer": response.get("response", "").strip()
        } 