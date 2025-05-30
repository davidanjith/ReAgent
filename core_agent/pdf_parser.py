import PyPDF2
import requests
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self, cache_dir: str = "paper_cache", parsed_dir: str = "parsed_papers"):
        self.cache_dir = Path(cache_dir)
        self.parsed_dir = Path(parsed_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.parsed_dir.mkdir(exist_ok=True)

    def download_pdf(self, url: str, paper_id: str) -> Optional[str]:
        """
        Download PDF from URL and save to cache
        """
        try:
            # Check if already cached
            cache_path = self.cache_dir / f"{paper_id}.pdf"
            if cache_path.exists():
                logger.info(f"Using cached PDF for {paper_id}")
                return str(cache_path)

            # Download PDF
            logger.info(f"Downloading PDF from {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Save to cache
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return str(cache_path)
        except Exception as e:
            logger.error(f"Error downloading PDF: {str(e)}")
            return None

    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        Parse PDF and extract structured information
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n"

                # Basic structure extraction
                sections = self._extract_sections(full_text)
                
                # Extract metadata
                metadata = {
                    "title": self._extract_title(full_text),
                    "authors": self._extract_authors(full_text),
                    "abstract": self._extract_abstract(full_text),
                    "sections": sections,
                    "references": self._extract_references(full_text),
                    "total_pages": len(reader.pages)
                }

                return metadata
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            return {}

    def _extract_title(self, text: str) -> str:
        """
        Extract paper title
        """
        # Usually the first non-empty line
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                return line.strip()
        return ""

    def _extract_authors(self, text: str) -> List[str]:
        """
        Extract author names
        """
        # Look for common author patterns
        lines = text.split('\n')
        authors = []
        for line in lines:
            if "et al." in line or "," in line:
                # Split by common delimiters
                names = line.replace("et al.", "").split(",")
                authors.extend([name.strip() for name in names if name.strip()])
        return authors

    def _extract_abstract(self, text: str) -> str:
        """
        Extract abstract section
        """
        # Look for common abstract markers
        abstract_markers = ["Abstract", "ABSTRACT"]
        lines = text.split('\n')
        abstract = []
        found_abstract = False
        
        for line in lines:
            if any(marker in line for marker in abstract_markers):
                found_abstract = True
                continue
            if found_abstract:
                if line.strip() and not line.strip().startswith(("1.", "Introduction")):
                    abstract.append(line.strip())
                else:
                    break
        
        return " ".join(abstract)

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract main sections and their content
        """
        sections = {}
        current_section = "Introduction"
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            # Check for section headers (numbered sections)
            if line.strip() and line.strip()[0].isdigit() and "." in line:
                if current_section and current_content:
                    sections[current_section] = " ".join(current_content)
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line.strip())
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = " ".join(current_content)
        
        return sections

    def _extract_references(self, text: str) -> List[str]:
        """
        Extract references section
        """
        references = []
        found_references = False
        
        lines = text.split('\n')
        for line in lines:
            if "References" in line or "Bibliography" in line:
                found_references = True
                continue
            if found_references and line.strip():
                if line.strip()[0].isdigit() or line.strip()[0] == "[":
                    references.append(line.strip())
        
        return references

    def process_paper(self, url: str, paper_id: str) -> Dict:
        """
        Download and process a paper, returning structured data
        """
        try:
            # Download PDF
            pdf_path = self.download_pdf(url, paper_id)
            if not pdf_path:
                logger.error(f"Failed to download PDF for paper {paper_id}")
                return {}

            # Parse PDF
            paper_data = self.parse_pdf(pdf_path)
            if not paper_data:
                logger.error(f"Failed to parse PDF for paper {paper_id}")
                return {}

            # Add metadata
            paper_data["paper_id"] = paper_id
            paper_data["pdf_url"] = url
            
            # Save parsed content to parsed_papers directory
            parsed_path = self.parsed_dir / f"{paper_id}_parsed.json"
            try:
                with open(parsed_path, 'w', encoding='utf-8') as f:
                    json.dump(paper_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved parsed content for paper {paper_id} to {parsed_path}")
            except Exception as e:
                logger.error(f"Failed to save parsed content for paper {paper_id}: {str(e)}")

            return paper_data
        except Exception as e:
            logger.error(f"Error processing paper {paper_id}: {str(e)}")
            return {} 