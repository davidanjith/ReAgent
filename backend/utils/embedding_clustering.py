from sentence_transformers import SentenceTransformer
import umap
import hdbscan
import numpy as np
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings

class EmbeddingClustering:
    def __init__(self):
        # Initialize the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            persist_directory="data/chroma"
        ))
        self.collection = self.chroma_client.get_or_create_collection(
            name="qa_pairs",
            metadata={"hnsw:space": "cosine"}
        )

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts)

    def cluster_embeddings(self, embeddings: np.ndarray) -> Tuple[np.ndarray, hdbscan.HDBSCAN]:
        """Cluster embeddings using UMAP + HDBSCAN."""
        # Reduce dimensionality with UMAP
        umap_reducer = umap.UMAP(
            n_neighbors=15,
            min_dist=0.0,
            n_components=2,
            random_state=42
        )
        umap_embeddings = umap_reducer.fit_transform(embeddings)
        
        # Cluster with HDBSCAN
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=2,
            min_samples=1,
            metric='euclidean'
        )
        cluster_labels = clusterer.fit_predict(umap_embeddings)
        
        return umap_embeddings, clusterer

    def store_qa_pair(self, question: str, answer: str, paper_id: str):
        """Store a Q&A pair in ChromaDB."""
        embedding = self.get_embeddings([question])[0]
        
        self.collection.add(
            embeddings=[embedding.tolist()],
            documents=[f"Q: {question}\nA: {answer}"],
            metadatas=[{
                "paper_id": paper_id,
                "type": "qa_pair"
            }],
            ids=[f"qa_{paper_id}_{len(self.collection.get()['ids'])}"]
        )

    def get_similar_qa_pairs(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve similar Q&A pairs from ChromaDB."""
        query_embedding = self.get_embeddings([query])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        return [
            {
                "text": doc,
                "metadata": meta
            }
            for doc, meta in zip(results['documents'][0], results['metadatas'][0])
        ]

    def get_cluster_hierarchy(self, embeddings: np.ndarray, clusterer: hdbscan.HDBSCAN) -> Dict:
        """Generate a hierarchical structure for visualization."""
        # Get cluster hierarchy from HDBSCAN
        hierarchy = clusterer.condensed_tree_.to_pandas()
        
        # Convert to a format suitable for D3 circle packing
        hierarchy_dict = {
            "name": "root",
            "children": []
        }
        
        # Process each cluster
        for cluster_id in set(clusterer.labels_):
            if cluster_id != -1:  # Skip noise points
                cluster_points = embeddings[clusterer.labels_ == cluster_id]
                cluster_dict = {
                    "name": f"cluster_{cluster_id}",
                    "children": [
                        {"name": f"point_{i}", "value": 1}
                        for i in range(len(cluster_points))
                    ]
                }
                hierarchy_dict["children"].append(cluster_dict)
        
        return hierarchy_dict 