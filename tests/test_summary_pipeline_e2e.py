from core_agent.summary_pipeline import summarize_topic
import json
from typing import Dict
import sys

def print_result(result: Dict, indent: int = 2) -> None:
    """Pretty print the result dictionary"""
    print("\n" + "="*80)
    print("SUMMARY PIPELINE RESULTS")
    print("="*80)
    
    # Print keywords
    print("\nExtracted Keywords:")
    print("-" * 40)
    for keyword in result["keywords"]:
        print(f"• {keyword}")
    
    # Print papers
    print("\nFound Papers:")
    print("-" * 40)
    for i, paper in enumerate(result["papers"], 1):
        print(f"\n{i}. Title: {paper.get('title', 'N/A')}")
        print(f"   Authors: {', '.join(paper.get('authors', ['N/A']))}")
        print(f"   Published: {paper.get('published', 'N/A')}")
        print(f"   Link: {paper.get('link', 'N/A')}")
        print(f"   Summary: {paper.get('summary', 'N/A')[:200]}...")
    
    # Print overall summary
    print("\nOverall Summary:")
    print("-" * 40)
    print(result["summary"])
    
    # Print any errors
    if "error" in result:
        print("\nErrors:")
        print("-" * 40)
        print(result["error"])

def main():
    # Test topic
    topic = "deep learning"
    print(f"\nTesting summarize pipeline with topic: {topic}")
    
    # Run the pipeline
    result = summarize_topic(topic, max_papers=5)
    
    # Print results
    print_result(result)
    
    # Verify requirements
    print("\nVerifying Requirements:")
    print("-" * 40)
    
    requirements = {
        "Has keywords": bool(result["keywords"]),
        "Has papers": bool(result["papers"]),
        "Has summary": bool(result["summary"]),
        "Paper count within limit": len(result["papers"]) <= 5,
        "Each paper has required fields": all(
            all(field in paper for field in ["title", "authors", "published", "link", "summary"])
            for paper in result["papers"]
        ),
        "No errors": "error" not in result
    }
    
    # Print requirement checks
    for req, status in requirements.items():
        print(f"✓ {req}: {'PASS' if status else 'FAIL'}")
    
    # Overall status
    all_passed = all(requirements.values())
    print(f"\nOverall Status: {'PASS' if all_passed else 'FAIL'}")

if __name__ == "__main__":
    main() 