"""
Tests for the embedding pipeline functionality.
"""

import pytest
from core_agent.embedding.embedding_pipeline import embed_and_store, batch_embed_and_store, EmbeddingError
from core_agent.embedding.ollama_embedder import OllamaEmbedder
from core_agent.vector_store.redis_store import RedisVectorStore

@pytest.fixture
def embedder():
    return OllamaEmbedder()

@pytest.fixture
def vector_store():
    return RedisVectorStore()

def test_embed_and_store_success(embedder, vector_store):
    """Test successful embedding and storage of a document."""
    text = "This is a test document for embedding."
    metadata = {"title": "Test Document", "type": "test"}
    
    doc_id = embed_and_store(text, metadata, embedder, vector_store)
    assert doc_id is not None
    
    # Verify storage
    stored_doc = vector_store.get_document(doc_id)
    assert stored_doc["text"] == text
    assert stored_doc["metadata"] == metadata
    assert stored_doc["embedding"] is not None

def test_embed_and_store_empty_text(embedder, vector_store):
    """Test handling of empty text."""
    with pytest.raises(ValueError):
        embed_and_store("", {"title": "Empty"}, embedder, vector_store)

def test_batch_embed_and_store(embedder, vector_store):
    """Test batch processing of documents."""
    texts = [
        "First test document.",
        "Second test document."
    ]
    metadata_list = [
        {"title": "First", "order": 1},
        {"title": "Second", "order": 2}
    ]
    
    doc_ids = batch_embed_and_store(texts, metadata_list, embedder, vector_store)
    assert len(doc_ids) == 2
    assert all(doc_id is not None for doc_id in doc_ids)
    
    # Verify storage
    for doc_id, text, metadata in zip(doc_ids, texts, metadata_list):
        stored_doc = vector_store.get_document(doc_id)
        assert stored_doc["text"] == text
        assert stored_doc["metadata"] == metadata
        assert stored_doc["embedding"] is not None

def test_batch_embed_and_store_mismatch(embedder, vector_store):
    """Test handling of mismatched texts and metadata."""
    with pytest.raises(ValueError):
        batch_embed_and_store(
            ["One document"],
            [{"title": "First"}, {"title": "Second"}],
            embedder,
            vector_store
        ) 