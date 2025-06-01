import fitz  # PyMuPDF
from typing import Dict, List, Optional
import arxiv
import requests
from pathlib import Path
import tempfile

class PaperProcessor:
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "research_companion"
        self.temp_dir.mkdir(exist_ok=True)

    async def download_arxiv_paper(self, arxiv_id: str) -> Path:
        """Download a paper from arXiv."""
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        # Download the PDF
        response = requests.get(paper.pdf_url)
        pdf_path = self.temp_dir / f"{arxiv_id}.pdf"
        
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        
        return pdf_path

    def extract_text(self, pdf_path: Path) -> Dict[str, str]:
        """Extract text from a PDF file."""
        doc = fitz.open(pdf_path)
        text_by_page = {}
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text_by_page[f"page_{page_num + 1}"] = text
        
        return text_by_page

    def extract_metadata(self, pdf_path: Path) -> Dict[str, str]:
        """Extract metadata from a PDF file."""
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
        }

    async def process_paper(self, source: str, arxiv_id: Optional[str] = None) -> Dict:
        """Process a paper from either a local file or arXiv."""
        if arxiv_id:
            pdf_path = await self.download_arxiv_paper(arxiv_id)
        else:
            pdf_path = Path(source)
        
        text_by_page = self.extract_text(pdf_path)
        metadata = self.extract_metadata(pdf_path)
        
        return {
            "metadata": metadata,
            "content": text_by_page,
            "source": str(pdf_path)
        } 