import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from utils.embedding_service import embedding_service

class MemoryService:
    def __init__(self):
        self.client = chromadb.Client()
        self.paper_collection = self.client.create_collection("papers")
        self.qa_collection = self.client.create_collection("qa_pairs")

    async def store_paper_chunks(self, paper_id: str, chunks: List[Dict[str, Any]]) -> None:
        """Store paper chunks with their embeddings."""
        ids = [f"{paper_id}_{i}" for i in range(len(chunks))]
        texts = [chunk['text'] for chunk in chunks]
        embeddings = [chunk['embedding'] for chunk in chunks]
        metadatas = [{"paper_id": paper_id, "chunk_index": i} for i in range(len(chunks))]
        
        self.paper_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    async def get_relevant_chunks(self, paper_id: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Get chunks relevant to the query."""
        query_embedding = await embedding_service.get_embedding(query)
        
        results = self.paper_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"paper_id": paper_id}
        )
        
        return [
            {
                "text": doc,
                "metadata": meta
            }
            for doc, meta in zip(results['documents'][0], results['metadatas'][0])
        ]

    async def store_qa_pair(self, paper_id: str, qa_id: str, question: str, answer: str, context: List[Dict[str, Any]]) -> None:
        """Store a Q&A pair with its context."""
        qa_text = f"Q: {question}\nA: {answer}"
        qa_embedding = await embedding_service.get_embedding(qa_text)
        
        self.qa_collection.add(
            ids=[qa_id],
            embeddings=[qa_embedding],
            documents=[qa_text],
            metadatas=[{
                "paper_id": paper_id,
                "question": question,
                "answer": answer,
                "context": [chunk['text'] for chunk in context]
            }]
        )

    async def get_paper_qa_pairs(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get all Q&A pairs for a paper."""
        results = self.qa_collection.get(
            where={"paper_id": paper_id}
        )
        
        return [
            {
                "id": id,
                "question": meta["question"],
                "answer": meta["answer"],
                "context": meta["context"]
            }
            for id, meta in zip(results['ids'], results['metadatas'])
        ]

    async def get_paper_clusters(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get clusters of Q&A pairs for a paper."""
        # Get all Q&A pairs for the paper
        qa_pairs = await self.get_paper_qa_pairs(paper_id)
        
        if not qa_pairs:
            return []
        
        # Get embeddings for all Q&A pairs
        embeddings = []
        for qa in qa_pairs:
            qa_text = f"Q: {qa['question']}\nA: {qa['answer']}"
            embedding = await embedding_service.get_embedding(qa_text)
            embeddings.append(embedding)
        
        # Use UMAP to reduce dimensionality
        import umap
        reducer = umap.UMAP(n_components=2, random_state=42)
        embeddings_2d = reducer.fit_transform(embeddings)
        
        # Use HDBSCAN for clustering
        import hdbscan
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
        cluster_labels = clusterer.fit_predict(embeddings_2d)
        
        # Group Q&A pairs by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label == -1:  # Noise points
                continue
            
            if label not in clusters:
                clusters[label] = []
            
            clusters[label].append(qa_pairs[i])
        
        return [
            {
                "id": str(label),
                "qa_pairs": qa_pairs
            }
            for label, qa_pairs in clusters.items()
        ]

# Create singleton instance
memory_service = MemoryService() 