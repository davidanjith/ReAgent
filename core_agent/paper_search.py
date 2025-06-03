import arxiv
from typing import List, Dict

import logging

logger = logging.getLogger(__name__)

class PaperSearch:
    def __init__(self):
        self.client = arxiv.Client()

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
            logger.info(f"Getting details for paper: {paper_id}")
            search = arxiv.Search(id_list=[paper_id])
            results = list(self.client.results(search))
            
            if not results:
                raise ValueError(f"No paper found with ID: {paper_id}")
                
            result = results[0]
            paper_details = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary,
                "pdf_url": result.pdf_url,
                "published": result.published.strftime("%Y-%m-%d"),
                "entry_id": result.entry_id,
                "categories": result.categories,
                "comment": result.comment,
                "journal_ref": result.journal_ref
            }
            logger.info(f"Retrieved details for paper: {paper_details['title']}")
            return paper_details
        except Exception as e:
            logger.error(f"Error in get_paper_details: {str(e)}")
            raise 