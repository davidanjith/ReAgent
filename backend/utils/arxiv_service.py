import arxiv
import asyncio
from typing import List, Dict, Any
import os
import json
from datetime import datetime

class ArxivService:
    def __init__(self):
        self.papers_dir = "test_data/papers"
        os.makedirs(self.papers_dir, exist_ok=True)

    async def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for papers on arXiv and download their content."""
        try:
            # Search arXiv
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            papers = []
            for result in search.results():
                # Download paper content
                paper_id = result.entry_id.split('/')[-1]
                paper_content = await self._download_paper(result)
                
                # Create paper metadata
                paper = {
                    'id': paper_id,
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'year': result.published.year,
                    'abstract': result.summary,
                    'citations': 0,  # arXiv doesn't provide citation count
                    'keywords': result.categories,
                    'url': result.entry_id,
                    'pdf_url': result.pdf_url
                }
                
                # Save paper content and metadata
                await self._save_paper(paper_id, paper_content, paper)
                papers.append(paper)

            return papers
        except Exception as e:
            print(f"Error searching arXiv: {str(e)}")
            return []

    async def _download_paper(self, result) -> str:
        """Download paper content from arXiv."""
        try:
            # For now, we'll just use the abstract as content
            # In a real implementation, you'd want to download and parse the PDF
            return result.summary
        except Exception as e:
            print(f"Error downloading paper: {str(e)}")
            return ""

    async def _save_paper(self, paper_id: str, content: str, metadata: Dict[str, Any]):
        """Save paper content and metadata to files."""
        try:
            # Save content
            content_file = os.path.join(self.papers_dir, f"{paper_id}.txt")
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Update metadata file
            metadata_file = os.path.join(self.papers_dir, "metadata.json")
            existing_metadata = []
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    existing_metadata = json.load(f)

            # Add new paper metadata
            existing_metadata.append(metadata)

            # Save updated metadata
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(existing_metadata, f, indent=4)

        except Exception as e:
            print(f"Error saving paper: {str(e)}")

arxiv_service = ArxivService() 