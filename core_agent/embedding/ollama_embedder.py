"""
OllamaEmbedder - A class for generating text embeddings using Ollama's local API.
"""

import requests
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class OllamaEmbedder:
    def __init__(self, model: str = "nomic-embed-text:v1.5", api_url: str = "http://localhost:11434/api/embeddings"):
        """
        Initialize the Ollama embedder.
        
        Args:
            model (str): The embedding model to use (default: "nomic-embed-text:v1.5")
            api_url (str): The Ollama API endpoint for embeddings
        """
        self.model = model
        self.api_url = api_url

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text input.
        
        Args:
            text (str): The text to generate embedding for
            
        Returns:
            Optional[List[float]]: The embedding vector if successful, None otherwise
        """
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]
            
            # Log embedding dimension for debugging
            print(f"Generated embedding with dimension: {len(embedding)}")
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None

    def get_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple text inputs.
        
        Args:
            texts (List[str]): List of texts to generate embeddings for
            
        Returns:
            List[Optional[List[float]]]: List of embedding vectors
        """
        return [self.get_embedding(text) for text in texts] 