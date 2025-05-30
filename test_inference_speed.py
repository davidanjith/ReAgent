import asyncio
import json
import time
from datetime import datetime
import requests
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Timer:
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"⏱️ {self.name}: {duration:.2f} seconds")

async def test_inference_speed():
    # Test query
    query = "machine learning applications in healthcare"
    max_results = 3  # Reduced for faster testing
    
    print(f"\n{'='*80}")
    print(f"Testing inference speed for query: {query}")
    print(f"{'='*80}")
    
    try:
        # Step 1: Search papers
        with Timer("Paper Search"):
            response = requests.post(
                "http://localhost:8000/search/",
                json={"query": query, "max_results": max_results}
            )
            response.raise_for_status()
            data = response.json()
        
        # Print results
        print("\n📊 Results:")
        print(f"Total papers found: {data['metadata']['total_papers']}")
        print(f"Total processing time: {data['metadata']['timestamp']}")
        
        # Print papers
        print("\n📚 Papers:")
        for i, paper in enumerate(data['papers'], 1):
            print(f"\nPaper {i}:")
            print(f"Title: {paper['title']}")
            print(f"Authors: {', '.join(paper['authors'])}")
            print(f"Published: {paper['published']}")
            print(f"Categories: {', '.join(paper['categories'])}")
            print(f"ID: {paper['paper_id']}")
            print("-" * 60)
        
        # Print summary
        print("\n📝 Generated Summary:")
        print(data['summary'])
        
        # Print knowledge graph stats
        print("\n🔍 Knowledge Graph:")
        print(f"Nodes: {len(data['knowledge_graph']['nodes'])}")
        print(f"Edges: {len(data['knowledge_graph']['edges'])}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
    except Exception as e:
        print(f"Error processing response: {str(e)}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("🔍 Testing Inference Speed")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    asyncio.run(test_inference_speed()) 