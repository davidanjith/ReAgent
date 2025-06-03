import numpy as np
import umap
import hdbscan
from typing import List, Dict, Any, Tuple
from datetime import datetime
import uuid

class ClusterService:
    def __init__(self):
        self.umap_reducer = umap.UMAP(
            n_neighbors=15,
            min_dist=0.1,
            n_components=2,
            metric='cosine'
        )
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=2,
            min_samples=1,
            metric='euclidean'
        )

    def cluster_embeddings(self, embeddings: List[List[float]]) -> Tuple[np.ndarray, np.ndarray]:
        """Cluster embeddings using UMAP + HDBSCAN."""
        # Reduce dimensionality with UMAP
        reduced_embeddings = self.umap_reducer.fit_transform(embeddings)
        
        # Cluster the reduced embeddings
        cluster_labels = self.clusterer.fit_predict(reduced_embeddings)
        
        return reduced_embeddings, cluster_labels

    def get_cluster_centroids(self, embeddings: List[List[float]], labels: np.ndarray) -> Dict[int, List[float]]:
        """Calculate centroids for each cluster."""
        centroids = {}
        unique_labels = np.unique(labels)
        
        for label in unique_labels:
            if label == -1:  # Skip noise points
                continue
            cluster_points = np.array([emb for i, emb in enumerate(embeddings) if labels[i] == label])
            centroids[label] = np.mean(cluster_points, axis=0).tolist()
        
        return centroids

    def create_cluster_metadata(self, qa_pairs: List[Dict[str, Any]], 
                              reduced_embeddings: np.ndarray,
                              cluster_labels: np.ndarray) -> List[Dict[str, Any]]:
        """Create metadata for each cluster."""
        clusters = {}
        
        for i, label in enumerate(cluster_labels):
            if label == -1:  # Skip noise points
                continue
                
            if label not in clusters:
                clusters[label] = {
                    'id': str(uuid.uuid4()),
                    'label': f"Cluster {label}",
                    'qa_ids': [],
                    'centroid': reduced_embeddings[i].tolist(),
                    'created_at': datetime.now().isoformat()
                }
            
            clusters[label]['qa_ids'].append(qa_pairs[i]['id'])
        
        return list(clusters.values())

    async def update_clusters(self, paper_id: str, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update clusters for a paper's Q&A pairs."""
        if not qa_pairs:
            return []

        # Get embeddings
        embeddings = [qa['embedding'] for qa in qa_pairs]
        
        # Perform clustering
        reduced_embeddings, cluster_labels = self.cluster_embeddings(embeddings)
        
        # Create cluster metadata
        clusters = self.create_cluster_metadata(qa_pairs, reduced_embeddings, cluster_labels)
        
        return clusters

cluster_service = ClusterService() 