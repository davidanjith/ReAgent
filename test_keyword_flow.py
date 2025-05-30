import logging
from core_agent.ollama_client import extract_keywords
from core_agent.utils.arxiv_api import search_arxiv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keyword_flow():
    # Test input
    test_input = "Recent advances in deep learning for computer vision"
    
    print("\n1. Testing keyword extraction:")
    print(f"Input text: {test_input}")
    
    # Extract keywords
    keywords = extract_keywords(test_input)
    print(f"\nExtracted keywords: {keywords}")
    
    print("\n2. Testing arXiv search with extracted keywords:")
    # Test with different query formats
    test_queries = [
        keywords,  # Original keywords
        [kw.replace("_", " ") for kw in keywords],  # Keywords with spaces
        ["deep learning", "computer vision", "machine learning"]  # Simple test keywords
    ]
    
    for i, query_keywords in enumerate(test_queries, 1):
        print(f"\nTest Query {i}:")
        print(f"Keywords: {query_keywords}")
        
        # Search arXiv with the keywords
        papers = search_arxiv(query_keywords)
        
        print(f"\nFound {len(papers)} papers:")
        for paper in papers:
            print(f"\nTitle: {paper['title']}")
            print(f"Authors: {', '.join(paper['authors'])}")
            print(f"Published: {paper['published']}")
            print("-" * 80)

if __name__ == "__main__":
    test_keyword_flow() 