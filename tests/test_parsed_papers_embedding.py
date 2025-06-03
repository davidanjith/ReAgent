"""
Test for storing parsed papers in Redis.
"""

import pytest
import json
import os
from pathlib import Path
from core_agent.embedding.embedding_pipeline import embed_and_store, batch_embed_and_store
from core_agent.embedding.ollama_embedder import OllamaEmbedder
from core_agent.vector_store.redis_store import RedisVectorStore

@pytest.fixture
def embedder():
    return OllamaEmbedder()

@pytest.fixture
def vector_store():
    return RedisVectorStore()

def load_parsed_papers(directory: str = None) -> list[dict]:
    """Load all parsed papers from the specified directory."""
    if directory is None:
        directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "parsed_papers")
    
    papers = []
    for file_path in Path(directory).glob("*_parsed.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            paper = json.load(f)
            paper['filename'] = file_path.name
            papers.append(paper)
    return papers

def test_store_papers(embedder, vector_store):
    """Test storing papers in Redis."""
    papers = load_parsed_papers()
    assert len(papers) > 0, "No parsed papers found"
    
    texts = []
    metadata_list = []
    
    for paper in papers:
        text = f"Title: {paper['title']}\nAbstract: {paper.get('abstract', '')}"
        texts.append(text)
        metadata_list.append({
            "title": paper["title"],
            "authors": paper.get("authors", []),
            "filename": paper["filename"],
            "source": "parsed_papers"
        })
    
    doc_ids = batch_embed_and_store(texts, metadata_list, embedder, vector_store)
    assert len(doc_ids) == len(papers), "Number of stored documents doesn't match number of papers"
    
    # Just check if embeddings exist in Redis
    for doc_id in doc_ids:
        stored_doc = vector_store.get_document(doc_id)
        assert stored_doc is not None, f"Document {doc_id} not found in Redis"
        assert stored_doc["embedding"] is not None, f"Embedding not found for document {doc_id}"
