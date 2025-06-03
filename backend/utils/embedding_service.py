from typing import List, Dict, Any
import numpy as np
from utils.ollama_interface import get_ollama_client

class EmbeddingService:
    def __init__(self):
        self.client = get_ollama_client()
        self.model = "llama2"  # or any other model that supports embeddings

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using Ollama."""
        return await self.client.generate_embedding(text)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            if embedding:
                embeddings.append(embedding)
        return embeddings

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    async def find_similar_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """Find most similar chunks to the query."""
        query_embedding = await self.get_embedding(query)
        if not query_embedding:
            return []

        # Calculate similarities
        similarities = []
        for chunk in chunks:
            similarity = self.cosine_similarity(query_embedding, chunk['embedding'])
            similarities.append((chunk, similarity))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in similarities[:top_k]]

# Create singleton instance
embedding_service = EmbeddingService() 