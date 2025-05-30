# Keyword extraction, ArXiv search and summarization
from typing import Dict, List, Optional
from core_agent.utils.arxiv_api import search_arxiv
from core_agent.ollama_client import extract_keywords, summarize_papers
from core_agent.pdf_parser import PDFParser
import logging
import json

logger = logging.getLogger(__name__)

def summarize_topic(user_input: str, max_papers: int = 5) -> Dict:
    """
    Full summarization pipeline that processes a topic and returns relevant paper summaries.
    
    Args:
        user_input (str): The topic or query to summarize
        max_papers (int, optional): Maximum number of papers to process. Defaults to 5.
    
    Returns:
        Dict containing:
            - keywords (List[str]): Extracted keywords from the input
            - papers (List[Dict]): List of paper metadata and content
            - summary (str): Combined summary of the papers
            - error (str, optional): Error message if something went wrong
    
    Raises:
        ValueError: If user_input is empty or invalid
    """
    if not user_input or not isinstance(user_input, str):
        raise ValueError("User input must be a non-empty string")

    try:
        # Initialize PDF parser
        pdf_parser = PDFParser()
        
        # Step 1: Extract keywords
        keywords = extract_keywords(user_input)
        if not keywords:
            return {
                "error": "Failed to extract keywords from input",
                "keywords": [],
                "papers": [],
                "summary": ""
            }

        # Step 2: Fetch papers from ArXiv using extracted keywords
        raw_papers = search_arxiv(keywords, max_results=max_papers)
        if not raw_papers:
            return {
                "error": "No papers found for the given keywords",
                "keywords": keywords,
                "papers": [],
                "summary": ""
            }

        # Step 3: Process each paper through PDF parser
        processed_papers = []
        for paper in raw_papers:
            try:
                # Extract paper ID and ensure we have required fields
                paper_id = paper.get('paper_id', '')
                if not paper_id:
                    logger.warning(f"Skipping paper without ID: {paper.get('title', 'Unknown')}")
                    continue

                # Download and parse PDF
                paper_data = pdf_parser.process_paper(paper.get('pdf_url', ''), paper_id)
                
                if paper_data:
                    # Combine metadata from search with parsed content
                    paper_data.update({
                        'title': paper.get('title', ''),
                        'authors': paper.get('authors', []),
                        'published': paper.get('published', ''),
                        'categories': paper.get('categories', []),
                        'abstract': paper.get('summary', ''),  # Use summary as abstract
                        'paper_id': paper_id,
                        'pdf_url': paper.get('pdf_url', '')
                    })
                    processed_papers.append(paper_data)
                    logger.info(f"Successfully processed paper: {paper.get('title', '')}")
                else:
                    # If PDF processing fails, include basic metadata
                    processed_papers.append({
                        'title': paper.get('title', ''),
                        'authors': paper.get('authors', []),
                        'published': paper.get('published', ''),
                        'categories': paper.get('categories', []),
                        'abstract': paper.get('summary', ''),  # Use summary as abstract
                        'paper_id': paper_id,
                        'pdf_url': paper.get('pdf_url', '')
                    })
                    logger.warning(f"PDF processing failed for paper: {paper.get('title', '')}")
            except Exception as e:
                logger.error(f"Error processing paper: {str(e)}")
                continue

        if not processed_papers:
            return {
                "error": "No papers could be processed successfully",
                "keywords": keywords,
                "papers": [],
                "summary": ""
            }

        # Step 4: Generate a single summary across all papers
        try:
            summary = summarize_papers(processed_papers)
            if not summary:
                return {
                    "error": "Failed to generate summary",
                    "keywords": keywords,
                    "papers": processed_papers,
                    "summary": ""
                }
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                "error": f"Error generating summary: {str(e)}",
                "keywords": keywords,
                "papers": processed_papers,
                "summary": ""
            }

        # Step 5: Return combined result
        return {
            "keywords": keywords,
            "papers": processed_papers,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Error in summarization pipeline: {str(e)}")
        return {
            "error": f"Error in summarization pipeline: {str(e)}",
            "keywords": [],
            "papers": [],
            "summary": ""
        }