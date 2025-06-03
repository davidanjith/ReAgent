import httpx
from typing import Dict, Any, List
import asyncio
from fastapi import HTTPException

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to Ollama with retries."""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError:
                if attempt == self.max_retries - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Could not connect to Ollama service. Please ensure it's running."
                    )
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
            except httpx.HTTPError as e:
                if attempt == self.max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error communicating with Ollama: {str(e)}"
                    )
                await asyncio.sleep(1 * (attempt + 1))

    async def chat(self, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send a chat request to Ollama."""
        return await self._make_request(
            "POST",
            "/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            }
        )

    async def generate_embedding(self, text: str, model: str = "llama2") -> List[float]:
        """Generate embeddings for text using Ollama."""
        response = await self._make_request(
            "POST",
            "/api/embeddings",
            json={
                "model": model,
                "prompt": text
            }
        )
        return response["embedding"]

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global client instance
_ollama_client = None

def get_ollama_client() -> OllamaClient:
    """Get an instance of the Ollama client."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client 