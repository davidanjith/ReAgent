import asyncio
import logging
import json
import os
from pathlib import Path
from core_agent.pdf_parser import PDFParser
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pdf_parser():
    # Initialize PDF parser
    parser = PDFParser()
    
    # Create parsed_papers directory if it doesn't exist
    parsed_papers_dir = Path("parsed_papers")
    parsed_papers_dir.mkdir(exist_ok=True)
    
    # Test paper URL and ID
    test_papers = [
        {
            "url": "https://arxiv.org/pdf/1706.03762.pdf",  # Attention is All You Need
            "id": "1706.03762"
        },
        {
            "url": "https://arxiv.org/pdf/2303.08774.pdf",  # Recent ML paper
            "id": "2303.08774"
        }
    ]
    
    for paper in test_papers:
        print(f"\n{'='*80}")
        print(f"Testing PDF parser for paper: {paper['id']}")
        print(f"{'='*80}")
        
        try:
            # Time the processing
            start_time = time.time()
            
            # Process the paper
            paper_data = parser.process_paper(paper['url'], paper['id'])
            
            # Save paper data to JSON file
            if paper_data:
                json_path = parsed_papers_dir / f"{paper['id']}.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(paper_data, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Saved paper data to {json_path}")
                
                # Print results
                print("\n📄 Paper Data:")
                print(f"Title: {paper_data.get('title', 'N/A')}")
                print(f"Authors: {', '.join(paper_data.get('authors', ['N/A']))}")
                print(f"Abstract: {paper_data.get('abstract', 'N/A')[:200]}...")
                print(f"Total Pages: {paper_data.get('total_pages', 'N/A')}")
                
                # Print sections
                print("\n📑 Sections:")
                for section, content in paper_data.get('sections', {}).items():
                    print(f"\n{section}:")
                    print(f"{content[:150]}...")
                
                # Print references
                print("\n📚 References:")
                for ref in paper_data.get('references', [])[:5]:  # Show first 5 references
                    print(f"- {ref}")
                
                print(f"\n⏱️ Processing time: {time.time() - start_time:.2f} seconds")
            else:
                print("❌ Failed to process paper")
                
        except Exception as e:
            print(f"❌ Error processing paper: {str(e)}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("🔍 Testing PDF Parser")
    asyncio.run(test_pdf_parser()) 