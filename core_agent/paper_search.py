import arxiv
from typing import List, Dict
from datetime import datetime
import logging
import asyncio
from typing import AsyncGenerator
import json

logger = logging.getLogger(__name__)

class PaperSearch:
    def __init__(self):
        self.client = arxiv.Client()
        self.paper_cache = {}

    async def search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for papers on arXiv based on the query
        """
        try:
            logger.info(f"Searching arXiv for: {query}")
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            # Get results synchronously since the client doesn't support async iteration
            results = list(self.client.results(search))
            
            papers = []
            for result in results:
                try:
                    paper = {
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "abstract": result.summary,
                        "pdf_url": result.pdf_url,
                        "published": result.published.strftime("%Y-%m-%d"),
                        "entry_id": result.entry_id,
                        "categories": result.categories
                    }
                    papers.append(paper)
                    logger.debug(f"Added paper: {paper['title']}")
                except Exception as e:
                    logger.error(f"Error processing paper result: {str(e)}")
                    continue

            logger.info(f"Found {len(papers)} papers")
            return papers
        except Exception as e:
            logger.error(f"Error in search_papers: {str(e)}")
            raise

    async def get_paper_details(self, paper_id: str) -> Dict:
        """
        Get detailed information about a specific paper
        """
        try:
            # Extract the arXiv ID from the full URL if present
            if paper_id.startswith('http'):
                paper_id = paper_id.split('/')[-1]
            
            # Remove version suffix if present
            if 'v' in paper_id:
                paper_id = paper_id.split('v')[0]
            
            # First try to get from cache
            if paper_id in self.paper_cache:
                return self.paper_cache[paper_id]
            
            # If not in cache, fetch from arXiv
            paper = await self.client.results(arxiv.Search(id_list=[paper_id]))
            paper = next(paper, None)
            
            if not paper:
                raise ValueError(f"Paper {paper_id} not found")
            
            # Get the full text
            try:
                full_text = await self._get_full_text(paper)
            except Exception as e:
                print(f"Error getting full text: {e}")
                full_text = paper.summary
            
            # Store in cache
            paper_data = {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.strftime("%Y-%m-%d"),
                "categories": paper.categories,
                "abstract": paper.summary,
                "full_text": full_text,
                "pdf_url": paper.pdf_url,
                "entry_id": paper.entry_id
            }
            self.paper_cache[paper_id] = paper_data
            
            return paper_data
            
        except Exception as e:
            print(f"Error getting paper details: {e}")
            raise

    async def _get_full_text(self, paper) -> str:
        """Get the full text of a paper"""
        try:
            # Try to get the full text from arXiv
            if hasattr(paper, 'full_text') and paper.full_text:
                return paper.full_text
            
            # If not available, try to get from PDF
            if paper.pdf_url:
                # Download and extract text from PDF
                # This is a placeholder - you'll need to implement PDF text extraction
                return paper.summary
            
            return paper.summary
        except Exception as e:
            print(f"Error getting full text: {e}")
            return paper.summary

    async def get_full_text(self, paper_id: str) -> Dict:
        """Get the full text of a paper"""
        try:
            paper_data = await self.get_paper_details(paper_id)
            return {"text": paper_data.get("full_text", paper_data["abstract"])}
        except Exception as e:
            print(f"Error getting full text: {e}")
            raise

    async def ingest_papers(self, papers: List[Dict]) -> Dict:
        """Ingest multiple papers and create a concept hierarchy"""
        try:
            # Get full text for each paper
            paper_texts = []
            for paper in papers:
                paper_id = paper["entry_id"]
                if paper_id.startswith('http'):
                    paper_id = paper_id.split('/')[-1]
                if 'v' in paper_id:
                    paper_id = paper_id.split('v')[0]
                
                paper_data = await self.get_paper_details(paper_id)
                paper_texts.append({
                    "title": paper_data["title"],
                    "text": paper_data.get("full_text", paper_data["abstract"])
                })
            
            # Create a prompt for the LLM to analyze the papers
            prompt = f"""
            Analyze these research papers and create a concept hierarchy:
            
            {json.dumps(paper_texts, indent=2)}
            
            Return a JSON object with:
            1. A list of main concepts (nodes)
            2. Relationships between concepts (edges)
            3. A brief summary of how these papers relate to each other
            """
            
            # Get analysis from LLM
            response = self.llm(prompt)
            try:
                analysis = json.loads(response)
            except:
                # Fallback to simple analysis if JSON parsing fails
                analysis = {
                    "nodes": [paper["title"] for paper in paper_texts],
                    "edges": [],
                    "summary": "Papers analyzed individually"
                }
            
            return analysis
            
        except Exception as e:
            print(f"Error ingesting papers: {e}")
            raise 