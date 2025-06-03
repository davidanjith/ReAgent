from typing import List, Dict, Any
import json
import os
from .ollama_interface import get_ollama_client

class PaperSearchService:
    def __init__(self):
        self.client = get_ollama_client()
        self.papers_dir = "test_data/papers"
        self.papers_metadata = self._load_papers_metadata()

    def _load_papers_metadata(self) -> List[Dict[str, Any]]:
        """Load papers metadata from the test data directory."""
        metadata_file = os.path.join(self.papers_dir, "metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return []

    async def search_papers(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant papers based on the query."""
        # Prepare the prompt for Ollama
        prompt = f"""Given the following research question: "{query}"
        Find the most relevant research papers from our collection that would help understand this topic.
        Consider papers that:
        1. Are fundamental to the field
        2. Provide clear explanations of key concepts
        3. Have high impact and are well-cited
        4. Are accessible to someone new to the topic

        Return a JSON array of paper IDs in order of relevance."""

        # Get response from Ollama
        response = await self.client.chat(
            model="llama2",
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            # Parse the response to get paper IDs
            paper_ids = json.loads(response.message.content)
            
            # Get paper details from metadata
            relevant_papers = []
            for paper_id in paper_ids[:top_k]:
                paper = next((p for p in self.papers_metadata if p['id'] == paper_id), None)
                if paper:
                    relevant_papers.append(paper)
            
            return relevant_papers
        except json.JSONDecodeError:
            # Fallback: return papers based on simple keyword matching
            return self._fallback_search(query, top_k)

    def _fallback_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback search method using simple keyword matching."""
        query_terms = query.lower().split()
        scored_papers = []

        for paper in self.papers_metadata:
            score = 0
            paper_text = f"{paper['title']} {paper.get('abstract', '')}".lower()
            
            for term in query_terms:
                if term in paper_text:
                    score += 1
            
            if score > 0:
                scored_papers.append((paper, score))

        # Sort by score and return top k
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        return [paper for paper, _ in scored_papers[:top_k]]

    def get_paper_content(self, paper_id: str) -> str:
        """Get the full content of a paper."""
        paper_file = os.path.join(self.papers_dir, f"{paper_id}.txt")
        if os.path.exists(paper_file):
            with open(paper_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

paper_search_service = PaperSearchService() 