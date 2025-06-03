"""
Test for fetching arXiv papers, generating embeddings, and storing in Redis.
"""

import pytest
import arxiv
import numpy as np
from core_agent.embedding.embedding_pipeline import embed_and_store, batch_embed_and_store
from core_agent.embedding.ollama_embedder import OllamaEmbedder
from core_agent.vector_store.redis_store import RedisVectorStore
import time

@pytest.fixture
def embedder():
    return OllamaEmbedder()

@pytest.fixture
def vector_store():
    return RedisVectorStore()

def verify_embedding_dimensions(embedding: list[float], expected_dim: int = 768):
    """Verify that the embedding has the expected dimensions."""
    if len(embedding) != expected_dim:
        raise ValueError(f"Embedding dimension mismatch. Expected {expected_dim}, got {len(embedding)}")
    return True

def test_embedding_dimensions_consistency(embedder):
    """Test that embedding dimensions remain constant regardless of input length."""
    # Test with very short text
    short_text = "Hello world"
    short_embedding = embedder.get_embedding(short_text)
    verify_embedding_dimensions(short_embedding)
    
    # Test with medium text
    medium_text = "This is a medium length text that contains more words and information than the short text."
    medium_embedding = embedder.get_embedding(medium_text)
    verify_embedding_dimensions(medium_embedding)
    
    # Test with very long text (concatenated multiple times)
    long_text = medium_text * 10
    long_embedding = embedder.get_embedding(long_text)
    verify_embedding_dimensions(long_embedding)
    
    # Verify all embeddings have the same dimension
    assert len(short_embedding) == len(medium_embedding) == len(long_embedding), \
        "Embedding dimensions should be consistent regardless of input length"
    
    print(f"\nEmbedding dimensions for different text lengths:")
    print(f"Short text ({len(short_text)} chars): {len(short_embedding)} dimensions")
    print(f"Medium text ({len(medium_text)} chars): {len(medium_embedding)} dimensions")
    print(f"Long text ({len(long_text)} chars): {len(long_embedding)} dimensions")

def fetch_arxiv_papers(query: str, max_results: int = 5):
    """
    Fetch papers from arXiv based on a search query.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of dictionaries containing paper information
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    for result in search.results():
        paper = {
            "title": result.title,
            "abstract": result.summary,
            "authors": [author.name for author in result.authors],
            "published": result.published.isoformat(),
            "arxiv_id": result.entry_id.split('/')[-1],
            "pdf_url": result.pdf_url
        }
        papers.append(paper)
    
    return papers

def test_arxiv_paper_embedding(embedder, vector_store):
    """Test fetching papers from arXiv and storing their embeddings."""
    # Search query for papers
    query = "get recent adavancements in neural networks"
    
    # Fetch papers
    papers = fetch_arxiv_papers(query, max_results=5)
    assert len(papers) > 0, "No papers found"
    
    # Prepare texts and metadata for embedding
    texts = []
    metadata_list = []
    
    for paper in papers:
        # Combine title and abstract for embedding
        text = f"Title: {paper['title']}\nAbstract: {paper['abstract']}"
        texts.append(text)
        
        # Store paper metadata
        metadata = {
            "title": paper["title"],
            "authors": paper["authors"],
            "published": paper["published"],
            "arxiv_id": paper["arxiv_id"],
            "pdf_url": paper["pdf_url"],
            "source": "arxiv"
        }
        metadata_list.append(metadata)
    
    # Generate embeddings and store in Redis
    doc_ids = batch_embed_and_store(texts, metadata_list, embedder, vector_store)
    
    # Verify storage
    assert len(doc_ids) == len(papers), "Number of stored documents doesn't match number of papers"
    assert all(doc_id is not None for doc_id in doc_ids), "Some documents failed to store"
    
    # Verify each stored document
    for doc_id, paper in zip(doc_ids, papers):
        stored_doc = vector_store.get_document(doc_id)
        
        # Verify text content
        assert paper["title"] in stored_doc["text"], "Title not found in stored text"
        assert paper["abstract"] in stored_doc["text"], "Abstract not found in stored text"
        
        # Verify metadata
        assert stored_doc["metadata"]["title"] == paper["title"]
        assert stored_doc["metadata"]["arxiv_id"] == paper["arxiv_id"]
        assert stored_doc["metadata"]["source"] == "arxiv"
        
        # Verify embedding
        assert stored_doc["embedding"] is not None, "Embedding not stored"
        assert len(stored_doc["embedding"]) > 0, "Empty embedding vector"
        verify_embedding_dimensions(stored_doc["embedding"])

def test_arxiv_paper_search(embedder, vector_store):
    """Test semantic search over stored arXiv papers."""
    # First, store some papers
    papers = fetch_arxiv_papers("machine learning", max_results=3)
    
    texts = []
    metadata_list = []
    for paper in papers:
        text = f"Title: {paper['title']}\nAbstract: {paper['abstract']}"
        texts.append(text)
        metadata_list.append({
            "title": paper["title"],
            "authors": paper["authors"],
            "arxiv_id": paper["arxiv_id"],
            "source": "arxiv"
        })
    
    # Store papers
    doc_ids = batch_embed_and_store(texts, metadata_list, embedder, vector_store)
    
    # Create a search query
    query = "deep learning applications in computer vision"
    query_embedding = embedder.get_embedding(query)
    assert query_embedding is not None, "Failed to generate query embedding"
    
    # Verify query embedding dimensions
    verify_embedding_dimensions(query_embedding)
    
    # Search for similar papers
    similar_docs = vector_store.search_similar(query_embedding, top_k=2)
    
    # Verify search results
    assert len(similar_docs) > 0, "No similar documents found"
    assert all("score" in doc for doc in similar_docs), "Missing similarity scores"
    assert all(doc["score"] > 0 for doc in similar_docs), "Invalid similarity scores"
    
    # Print search results for inspection
    print("\nSearch Results:")
    for doc in similar_docs:
        print(f"\nTitle: {doc['metadata']['title']}")
        print(f"Score: {doc['score']:.4f}")
        print(f"Authors: {', '.join(doc['metadata']['authors'])}") 