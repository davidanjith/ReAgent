import uuid
from typing import List, Optional, Dict
from datetime import datetime
from models.paper import Paper, PaperCreate, PaperUpdate

class PaperService:
    def __init__(self):
        self.papers = {}  # In-memory storage for papers

    def create_paper(self, paper: PaperCreate) -> Paper:
        paper_id = str(uuid.uuid4())
        new_paper = Paper(
            id=paper_id,
            **paper.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.papers[paper_id] = new_paper
        return new_paper

    def get_paper(self, paper_id: str) -> Optional[Paper]:
        return self.papers.get(paper_id)

    def get_all_papers(self) -> List[Paper]:
        return list(self.papers.values())

    def update_paper(self, paper_id: str, paper_update: PaperUpdate) -> Optional[Paper]:
        if paper_id not in self.papers:
            return None
        
        paper = self.papers[paper_id]
        update_data = paper_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(paper, field, value)
        
        paper.updated_at = datetime.utcnow()
        return paper

    def delete_paper(self, paper_id: str) -> bool:
        if paper_id in self.papers:
            del self.papers[paper_id]
            return True
        return False

    def search_papers(self, query: str) -> List[Paper]:
        """Search papers by title, authors, or content."""
        query = query.lower()
        return [
            paper for paper in self.papers.values()
            if query in paper.title.lower() or
               query in paper.content.lower() or
               any(query in author.lower() for author in paper.authors)
        ]

    def split_into_chunks(self, text: str, chunk_size: int = 1000) -> List[Dict[str, str]]:
        """Split text into chunks of approximately equal size."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
            
            if current_size >= chunk_size:
                chunks.append({
                    'text': ' '.join(current_chunk)
                })
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append({
                'text': ' '.join(current_chunk)
            })
        
        return chunks

# Create singleton instance
paper_service = PaperService() 