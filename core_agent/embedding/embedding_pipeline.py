"""
Embedding Pipeline - A module for processing and storing document embeddings using Ollama and Redis.
"""

from typing import Dict, Any, Optional
import numpy as np
from .ollama_embedder import OllamaEmbedder
from ..vector_store.redis_store import RedisVectorStore

class EmbeddingError(Exception):
    """Exception raised when embedding generation fails."""
    pass

def embed_and_store(
    text: str,
    metadata: Dict[str, Any],
    embedder: Optional[OllamaEmbedder] = None,
    vector_store: Optional[RedisVectorStore] = None
) -> str:
    """
    Generate embedding for text and store it along with metadata in Redis.
    
    Args:
        text (str): The text to generate embedding for
        metadata (Dict[str, Any]): Additional metadata to store with the document
        embedder (Optional[OllamaEmbedder]): Optional OllamaEmbedder instance
        vector_store (Optional[RedisVectorStore]): Optional RedisVectorStore instance
        
    Returns:
        str: The UUID of the stored document
        
    Raises:
        EmbeddingError: If embedding generation fails
        ValueError: If text is empty or None
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
        
    # Initialize components if not provided
    if embedder is None:
        embedder = OllamaEmbedder()
    if vector_store is None:
        vector_store = RedisVectorStore()
        
    # Generate embedding
    embedding = embedder.get_embedding(text)
    if embedding is None:
        raise EmbeddingError("Failed to generate embedding for the text")
        
    # Convert to float32 for consistency
    embedding = np.array(embedding, dtype=np.float32).tolist()
    
    # Store in Redis
    doc_id = vector_store.store_document(text, embedding, metadata)
    return doc_id

def batch_embed_and_store(
    texts: list[str],
    metadata_list: list[Dict[str, Any]],
    embedder: Optional[OllamaEmbedder] = None,
    vector_store: Optional[RedisVectorStore] = None
) -> list[str]:
    """
    Process multiple documents in batch.
    
    Args:
        texts (list[str]): List of texts to process
        metadata_list (list[Dict[str, Any]]): List of metadata dictionaries
        embedder (Optional[OllamaEmbedder]): Optional OllamaEmbedder instance
        vector_store (Optional[RedisVectorStore]): Optional RedisVectorStore instance
        
    Returns:
        list[str]: List of document UUIDs
        
    Raises:
        ValueError: If texts and metadata lists have different lengths
    """
    if len(texts) != len(metadata_list):
        raise ValueError("Number of texts must match number of metadata entries")
        
    # Initialize components if not provided
    if embedder is None:
        embedder = OllamaEmbedder()
    if vector_store is None:
        vector_store = RedisVectorStore()
        
    doc_ids = []
    for text, metadata in zip(texts, metadata_list):
        try:
            doc_id = embed_and_store(text, metadata, embedder, vector_store)
            doc_ids.append(doc_id)
        except (EmbeddingError, ValueError) as e:
            print(f"Error processing document: {str(e)}")
            doc_ids.append(None)
            
    return doc_ids 