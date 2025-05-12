import arxiv
from typing import List, Dict, Optional
from datetime import datetime
import logging
import asyncio
from typing import AsyncGenerator
import json
from langchain_community.llms import Ollama
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import tempfile
import os
import re

logger = logging.getLogger(__name__)

class PaperSearch:
    def __init__(self):
        self.client = arxiv.Client()
        self.paper_cache = {}
        # Initialize LLM
        self.llm = Ollama(
            model="llama2:latest",
            temperature=0.7,
            stop=["Human:", "Assistant:"],
            timeout=30
        )

    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search arXiv for papers matching the query
        """
        try:
            logger.info(f"Searching arXiv for: {query}")
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            # Get results as a list first
            results = list(self.client.results(search))
            
            # Process the results
            papers = []
            for result in results:
                paper = {
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'published': result.published.strftime('%Y-%m-%d'),
                    'categories': result.categories,
                    'entry_id': result.entry_id,
                    'pdf_url': result.pdf_url
                }
                papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers")
            return papers
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {str(e)}")
            raise

    async def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific paper
        """
        try:
            # Check cache first
            if paper_id in self.paper_cache:
                return self.paper_cache[paper_id]

            search = arxiv.Search(id_list=[paper_id])
            results = list(self.client.results(search))
            if results:
                result = results[0]
                paper_data = {
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'published': result.published.strftime('%Y-%m-%d'),
                    'categories': result.categories,
                    'entry_id': result.entry_id,
                    'pdf_url': result.pdf_url
                }
                # Cache the result
                self.paper_cache[paper_id] = paper_data
                return paper_data
            return None
            
        except Exception as e:
            logger.error(f"Error getting paper details: {str(e)}")
            raise

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF content with improved space handling and error recovery
        """
        try:
            # Create a temporary file to store the PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name

            try:
                # Open the PDF
                with open(temp_file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    # Process each page
                    for page in reader.pages:
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                # Fix common spacing issues
                                # Add space between words that are too close
                                page_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', page_text)
                                # Add space after punctuation if missing
                                page_text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', page_text)
                                # Fix common word combinations
                                page_text = re.sub(r'([a-z])([0-9])', r'\1 \2', page_text)
                                page_text = re.sub(r'([0-9])([a-z])', r'\1 \2', page_text)
                                # Fix common LaTeX artifacts
                                page_text = re.sub(r'\\[a-zA-Z]+', '', page_text)
                                page_text = re.sub(r'\{|\}', '', page_text)
                                
                                text += page_text + "\n"
                        except Exception as e:
                            logger.warning(f"Error extracting text from page: {str(e)}")
                            continue

                if not text.strip():
                    logger.warning("No text could be extracted from PDF")
                    return None

                return text.strip()
                
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Error deleting temporary file: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None

    async def get_full_text(self, paper_id: str) -> Optional[Dict]:
        """
        Get the full text of a paper and create a concept hierarchy
        """
        try:
            paper = await self.get_paper_details(paper_id)
            if not paper:
                return None

            # Try to get the full text from arXiv
            try:
                # Download the PDF
                response = requests.get(paper['pdf_url'])
                response.raise_for_status()
                
                # Extract text from the PDF
                full_text = self._extract_text_from_pdf(response.content)
                
                if full_text:
                    # Create concept hierarchy
                    hierarchy = await self._create_concept_hierarchy(full_text, paper['title'], paper['abstract'])
                    return {
                        "text": full_text,
                        "hierarchy": hierarchy
                    }
                else:
                    logger.warning("Could not extract text from PDF, falling back to abstract")
                    hierarchy = await self._create_concept_hierarchy(paper['abstract'], paper['title'], paper['abstract'])
                    return {
                        "text": paper['abstract'],
                        "hierarchy": hierarchy
                    }
                    
            except Exception as e:
                logger.warning(f"Could not fetch full text: {str(e)}")
                hierarchy = await self._create_concept_hierarchy(paper['abstract'], paper['title'], paper['abstract'])
                return {
                    "text": paper['abstract'],
                    "hierarchy": hierarchy
                }
            
        except Exception as e:
            logger.error(f"Error getting full text: {str(e)}")
            raise

    async def _create_concept_hierarchy(self, text: str, title: str, abstract: str = None) -> Dict:
        """
        Create a concept hierarchy: root is paper title, children are Outline, Abstract, and main concepts.
        """
        try:
            # 1. Generate outline/summary from the full text (or abstract if full text is not available)
            outline_prompt = f"""
            Summarize the following research paper in a concise outline (3-5 bullet points) covering the main idea, methodology, and findings. Return only the summary as a single string.
            ---
            {text}
            """
            outline = self.llm(outline_prompt).strip()

            # 2. Extract main concepts as before (from full text or abstract)
            concept_prompt = f"""
            Extract the main concepts, topics, or sections from the following research paper text. Return a JSON array of objects with 'name' and 'summary' fields. Each object should represent a key concept or section.
            ---
            {text}
            """
            try:
                concepts_response = self.llm(concept_prompt).strip()
                if concepts_response.startswith('```json'):
                    concepts_response = concepts_response[7:]
                if concepts_response.endswith('```'):
                    concepts_response = concepts_response[:-3]
                concepts_response = concepts_response.strip()
                main_concepts = json.loads(concepts_response)
            except Exception as e:
                logger.error(f"Failed to parse main concepts: {str(e)} | Raw: {concepts_response}")
                # Fallback: treat the response as a single summary concept
                main_concepts = [{"name": "Main Concepts", "summary": concepts_response}]

            # 3. Build hierarchy
            children = [
                {"name": "Outline", "summary": outline, "value": 1},
            ]
            if abstract:
                children.append({"name": "Abstract", "summary": abstract, "value": 1})
            for c in main_concepts:
                children.append({"name": c.get("name", "Concept"), "summary": c.get("summary", ""), "value": 1})

            return {
                "name": title,
                "children": children
            }
        except Exception as e:
            logger.error(f"Error creating concept hierarchy: {str(e)}")
            return self._create_fallback_hierarchy(title)

    def _create_fallback_hierarchy(self, title: str) -> Dict:
        """Create a fallback hierarchy when the main process fails"""
        return {
            "name": title,
            "children": [
                {
                    "name": "Abstract",
                    "summary": "Paper abstract",
                    "children": [
                        {"name": "Key Concepts", "summary": "Main concepts from the paper", "value": 1},
                        {"name": "Methodology", "summary": "Research approach and methods", "value": 1},
                        {"name": "Findings", "summary": "Key findings and results", "value": 1}
                    ]
                }
            ]
        }

    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        """
        Split text into chunks while trying to preserve sentence boundaries
        """
        chunks = []
        current_chunk = ""
        
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    async def chat_about_paper(self, paper_id: str, message: str) -> Dict:
        """
        Chat about a specific paper
        """
        try:
            paper = await self.get_paper_details(paper_id)
            if not paper:
                raise ValueError(f"Paper {paper_id} not found")

            # Get full text for better context
            full_text = await self.get_full_text(paper_id)
            context = full_text if full_text else paper['abstract']

            # Create a prompt for the chat
            prompt = f"""You are an AI research assistant helping to analyze and discuss academic papers.
            You have access to the following paper information:
            
            Title: {paper['title']}
            Authors: {', '.join(paper['authors'])}
            Abstract: {paper['abstract']}
            
            Full Text: {context[:2000]}  # Limit context to first 2000 chars to avoid token limits
            
            Human: {message}
            Assistant:"""

            # Get response from LLM
            response = self.llm(prompt)
            
            return {
                "response": response,
                "paper": paper
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
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
                if paper_data:
                    # Get full text
                    full_text = await self.get_full_text(paper_id)
                    paper_texts.append({
                        "title": paper_data["title"],
                        "text": full_text if full_text else paper_data["abstract"]
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
            logger.error(f"Error ingesting papers: {str(e)}")
            raise 