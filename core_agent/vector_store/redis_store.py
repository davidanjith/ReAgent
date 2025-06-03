"""
RedisVectorStore - A class for storing and retrieving embeddings and metadata in Redis.
"""

import json
import uuid
from typing import Dict, List, Optional, Any
import redis
import numpy as np

class RedisVectorStore:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize the Redis vector store.
        
        Args:
            host (str): Redis host (default: "localhost")
            port (int): Redis port (default: 6379)
            db (int): Redis database number (default: 0)
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.vector_client = redis.Redis(host=host, port=port, db=db)  # For binary data

    def store_document(self, text: str, embedding: List[float], metadata: Dict[str, Any] = None) -> str:
        """
        Store a document with its embedding and metadata in Redis.
        
        Args:
            text (str): The document text
            embedding (List[float]): The document's embedding vector
            metadata (Dict[str, Any], optional): Additional metadata to store
            
        Returns:
            str: The generated UUID for the document
        """
        doc_id = str(uuid.uuid4())
        
        # Store embedding as binary data
        self.vector_client.set(f"embedding:{doc_id}", np.array(embedding).tobytes())
        
        # Store text and metadata as JSON
        self.redis_client.set(f"text:{doc_id}", text)
        if metadata:
            self.redis_client.set(f"meta:{doc_id}", json.dumps(metadata))
            
        return doc_id

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieve a document and its associated data from Redis.
        
        Args:
            doc_id (str): The document's UUID
            
        Returns:
            Dict[str, Any]: Dictionary containing the document's text, embedding, and metadata
        """
        result = {
            "text": self.redis_client.get(f"text:{doc_id}"),
            "embedding": None,
            "metadata": None
        }
        
        # Get embedding
        embedding_bytes = self.vector_client.get(f"embedding:{doc_id}")
        if embedding_bytes:
            result["embedding"] = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()
            
        # Get metadata
        metadata_json = self.redis_client.get(f"meta:{doc_id}")
        if metadata_json:
            result["metadata"] = json.loads(metadata_json)
            
        return result

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query_embedding (List[float]): The query embedding vector
            top_k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of similar documents with their scores
        """
        query_vector = np.array(query_embedding)
        results = []
        
        # Get all embedding keys
        embedding_keys = self.vector_client.keys("embedding:*")
        
        for key in embedding_keys:
            doc_id = key.decode('utf-8').split(':')[1]
            embedding_bytes = self.vector_client.get(key)
            
            if embedding_bytes:
                stored_vector = np.frombuffer(embedding_bytes, dtype=np.float32)
                
                # Calculate cosine similarity
                similarity = np.dot(query_vector, stored_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(stored_vector)
                )
                
                # Get document data
                doc_data = self.get_document(doc_id)
                doc_data["score"] = float(similarity)
                results.append(doc_data)
        
        # Sort by similarity score and return top_k results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its associated data from Redis.
        
        Args:
            doc_id (str): The document's UUID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.vector_client.delete(f"embedding:{doc_id}")
            self.redis_client.delete(f"text:{doc_id}")
            self.redis_client.delete(f"meta:{doc_id}")
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {str(e)}")
            return False 