import asyncio
from core_agent.paper_search import PaperSearch

async def test_arxiv():
    search = PaperSearch()
    try:
        results = await search.search_papers('machine learning', max_results=2)
        print("\nSearch Results:")
        for paper in results:
            print(f"\nTitle: {paper['title']}")
            print(f"Authors: {', '.join(paper['authors'])}")
            print(f"Published: {paper['published']}")
            print(f"PDF URL: {paper['pdf_url']}")
            print("-" * 80)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_arxiv()) 