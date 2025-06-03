"""
PaperChat - A specialized chat system for interacting with paper documents using embeddings and vector search.
"""

import requests
from typing import List, Dict, Optional, Any
from .embedding.ollama_embedder import OllamaEmbedder
from .vector_store.redis_store import RedisVectorStore

class PaperChat:
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434/api/generate",
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 redis_db: int = 0):
        """
        Initialize the PaperChat system.
        
        Args:
            ollama_url (str): URL for Ollama's generate API
            redis_host (str): Redis host
            redis_port (int): Redis port
            redis_db (int): Redis database number
        """
        self.ollama_url = ollama_url
        self.embedder = OllamaEmbedder()
        self.vector_store = RedisVectorStore(host=redis_host, port=redis_port, db=redis_db)

    def _query_ollama(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and get the response.
        
        Args:
            prompt (str): The prompt to send to Ollama
            
        Returns:
            str: Ollama's response
        """
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": "llama2:latest",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error querying Ollama: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."

    def _construct_prompt(self, question: str, documents: List[Dict[str, Any]]) -> str:
        """
        Construct a prompt combining the question and retrieved documents.
        
        Args:
            question (str): The user's question
            documents (List[Dict[str, Any]]): List of retrieved documents with their content
            
        Returns:
            str: The constructed prompt
        """
        # Start with context from documents
        context = "Based on the following documents:\n\n"
        for i, doc in enumerate(documents, 1):
            context += f"Document {i}:\n{doc['text']}\n\n"
        
        # Add the question
        prompt = f"{context}Question: {question}\n\nPlease provide a detailed answer based on the documents above. If the documents don't contain enough information to answer the question, please say so.\n\nAnswer:"
        return prompt

    def chat_with_papers(self, question: str, multi_doc: bool = False) -> str:
        """
        Chat with papers by retrieving relevant documents and generating a response.
        
        Args:
            question (str): The user's question
            multi_doc (bool): Whether to retrieve multiple documents (True) or just the most relevant one (False)
            
        Returns:
            str: The generated response
        """
        # Get embedding for the question
        question_embedding = self.embedder.get_embedding(question)
        if not question_embedding:
            return "I apologize, but I encountered an error while processing your question."

        # Retrieve relevant documents
        top_k = 3 if multi_doc else 1
        relevant_docs = self.vector_store.search_similar(question_embedding, top_k=top_k)
        
        if not relevant_docs:
            return "I couldn't find any relevant documents to answer your question."

        # Construct and send prompt to Ollama
        prompt = self._construct_prompt(question, relevant_docs)
        response = self._query_ollama(prompt)
        
        return response 