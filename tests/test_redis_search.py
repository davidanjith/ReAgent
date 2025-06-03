from core_agent.vector_store.redis_store import RedisVectorStore
from core_agent.embedding.ollama_embedder import OllamaEmbedder
import numpy as np

def test_search():
    # Initialize components
    vector_store = RedisVectorStore()
    embedder = OllamaEmbedder()
    
    # Test data
    test_texts = [
        "This is a test document about machine learning",
        "Python programming language is widely used",
        "Deep learning models require large datasets",
        "Natural language processing is a subfield of AI"
    ]
    
    # Store test documents
    print("\n=== Storing Test Documents ===")
    doc_ids = []
    for i, text in enumerate(test_texts):
        # Generate embedding
        embedding = embedder.get_embedding(text)
        if embedding:
            # Store with metadata
            doc_id = vector_store.store_document(
                text=text,
                embedding=embedding,
                metadata={
                    "paper_id": "test_paper",
                    "section": f"test_section_{i}",
                    "title": "Test Document"
                }
            )
            doc_ids.append(doc_id)
            print(f"Stored document {i+1} with ID: {doc_id}")
    
    # Test search with a query
    print("\n=== Testing Search ===")
    query = "Tell me about machine learning"
    query_embedding = embedder.get_embedding(query)
    
    if query_embedding:
        print(f"\nSearching for: {query}")
        results = vector_store.search_similar(
            query_embedding=query_embedding,
            paper_id="test_paper",
            top_k=2
        )
        
        print("\n=== Search Results ===")
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Score: {result['score']}")
            print(f"Text: {result['text']}")
            print(f"Section: {result['metadata']['section']}")
    
    # Cleanup
    print("\n=== Cleaning Up ===")
    for doc_id in doc_ids:
        vector_store.delete_document(doc_id)
        print(f"Deleted document: {doc_id}")

if __name__ == "__main__":
    test_search() 