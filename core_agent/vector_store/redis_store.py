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

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1 (List[float]): First vector
            vec2 (List[float]): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

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
        print(f"Storing document with ID: {doc_id}")
        print(f"Embedding dimension: {len(embedding)}")
        
        # Store embedding as binary data
        embedding_array = np.array(embedding, dtype=np.float32)
        self.vector_client.set(f"embedding:{doc_id}", embedding_array.tobytes())
        
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

    def search_similar(self, query_embedding: List[float], paper_id: str = None, top_k: int = 5, similarity_threshold: float = 0.3) -> List[Dict]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query_embedding (List[float]): The query embedding vector
            paper_id (str, optional): Filter results to this paper ID
            top_k (int): Number of top results to return
            similarity_threshold (float): Minimum cosine similarity score to consider a result relevant (default: 0.3)
            
        Returns:
            List[Dict]: List of similar documents with their metadata and scores
        """
        try:
            # Debug: Print all keys in Redis
            print("\n=== Redis Debug Info ===")
            all_keys = self.vector_client.keys("*")
            print(f"All keys in Redis: {[k.decode('utf-8') for k in all_keys]}")
            
            # Get all document IDs from embedding keys
            doc_ids = self.vector_client.keys("embedding:*")
            print(f"\nFound {len(doc_ids)} embedding documents in Redis")
            
            if not doc_ids:
                print("No documents found in Redis")
                return []
            
            # Debug: Print first few embeddings
            print("\n=== Sample Embeddings ===")
            for key in doc_ids[:2]:  # Look at first 2 embeddings
                doc_id = key.decode('utf-8').split(':')[1]
                embedding_bytes = self.vector_client.get(key)
                if embedding_bytes:
                    embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                    print(f"Doc {doc_id} embedding shape: {embedding.shape}")
                    print(f"First few values: {embedding[:5]}")
            
            print(f"\nQuery embedding shape: {len(query_embedding)}")
            print(f"Query embedding first few values: {query_embedding[:5]}")
            print(f"\nUsing similarity threshold: {similarity_threshold}")
            
            # Calculate similarities
            similarities = []
            for key in doc_ids:
                doc_id = key.decode('utf-8').split(':')[1]
                
                # Get document metadata first to filter by paper_id
                metadata = self.redis_client.get(f"meta:{doc_id}")
                if not metadata:
                    print(f"No metadata found for {doc_id}")
                    continue
                    
                metadata = json.loads(metadata)
                if paper_id and metadata.get("paper_id") != paper_id:
                    continue
                
                print(f"\nProcessing document {doc_id}")
                print(f"Metadata: {metadata}")
                
                # Get document embedding
                embedding_bytes = self.vector_client.get(key)
                if not embedding_bytes:
                    print(f"No embedding found for {doc_id}")
                    continue
                    
                doc_embedding = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()
                print(f"Retrieved embedding with dimension: {len(doc_embedding)}")
                
                # Check for dimension mismatch
                if len(doc_embedding) != len(query_embedding):
                    print(f"Warning: Dimension mismatch for doc {doc_id}. Query: {len(query_embedding)}, Stored: {len(doc_embedding)}")
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                print(f"Calculated similarity score: {similarity}")
                
                # Only include results above the threshold
                if similarity < similarity_threshold:
                    print(f"Skipping document {doc_id} due to low similarity score")
                    continue
                
                # Get document text
                text = self.redis_client.get(f"text:{doc_id}")
                if text:
                    print(f"Retrieved text of length: {len(text)}")
                    print(f"Text preview: {text[:100]}...")
                else:
                    print(f"No text found for {doc_id}")
                    continue
                
                similarities.append({
                    "doc_id": doc_id,
                    "score": similarity,
                    "metadata": metadata,
                    "text": text
                })
            
            print(f"\nFound {len(similarities)} similar documents above threshold {similarity_threshold}")
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x["score"], reverse=True)
            
            # Debug: Print top results
            print("\n=== Top Results ===")
            for i, sim in enumerate(similarities[:top_k]):
                print(f"Result {i+1}:")
                print(f"Doc ID: {sim['doc_id']}")
                print(f"Score: {sim['score']}")
                print(f"Section: {sim['metadata'].get('section', 'Unknown')}")
                print(f"Text preview: {sim['text'][:100]}...")
            
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Error in search_similar: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return []

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