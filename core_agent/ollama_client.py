# Handles interaction with Ollama (LLM backend)

import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

OLLAMA_API = os.getenv("OLLAMA_URL")
MODEL = os.getenv("OLLAMA_MODEL")


def query_ollama(prompt: str) -> str:
    response = requests.post(OLLAMA_API, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_gpu": 1,  # Enable GPU acceleration
            "num_thread": 16  # Adjust based on your CPU cores
        }
    })
    response.raise_for_status()
    return response.json()["response"].strip()


def extract_keywords(text: str) -> list[str]:
    prompt = (
        "Extract 3-5 most relevant academic keywords from the following query that would be useful for searching research papers. "
        "Focus on technical terms, scientific concepts, and research areas. "
        "Ignore common words, verbs, and non-technical terms.\n\n"
        f"Query: \"{text}\"\n\n"
        "Return only a comma-separated list of keywords. "
        "Each keyword should be a single technical term or concept. "
        "Use underscores for multi-word terms. "
        "Do not include any explanations or extra text."
    )
    
    try:
        response = query_ollama(prompt)
        # Clean and validate the response
        keywords = []
        for line in response.splitlines():
            if ',' in line:
                # Split by comma and clean each keyword
                raw_keywords = [kw.strip().lower() for kw in line.split(',')]
                # Filter out common words and ensure minimum length
                filtered_keywords = [
                    kw for kw in raw_keywords 
                    if len(kw) > 3 and not kw in ['the', 'and', 'for', 'with', 'from', 'this', 'that']
                ]
                keywords.extend(filtered_keywords)
                break
        
        # If no valid keywords found in lines with commas, try splitting the whole response
        if not keywords:
            keywords = [kw.strip().lower() for kw in response.split(',') 
                       if len(kw.strip()) > 3 and not kw.strip() in ['the', 'and', 'for', 'with', 'from', 'this', 'that']]
        
        # Ensure we have at least 2 keywords
        if len(keywords) < 2:
            # Fallback to basic keyword extraction with better filtering
            words = text.lower().split()
            common_words = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'what', 'how', 'why', 'when', 'where', 'which', 'who'}
            keywords = [word for word in words if len(word) > 3 and word not in common_words][:3]
        
        # Remove duplicates while preserving order
        seen = set()
        keywords = [kw for kw in keywords if not (kw in seen or seen.add(kw))]
        
        return keywords[:3]  # Limit to 3 most relevant keywords
        
    except Exception as e:
        print(f"Error in keyword extraction: {str(e)}")
        # Fallback to basic keyword extraction with better filtering
        words = text.lower().split()
        common_words = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'what', 'how', 'why', 'when', 'where', 'which', 'who'}
        return [word for word in words if len(word) > 3 and word not in common_words][:3]


def summarize_papers(papers: list[dict]) -> str:
    try:
        if not papers:
            return "No papers available for summarization."

        # Collecting the titles and abstracts of the papers to create a prompt for summarization
        paper_details = []
        for paper in papers:
            try:
                # Get paper metadata with fallbacks
                title = paper.get('title', 'Unknown Title')
                abstract = paper.get('abstract', '')
                if not abstract:
                    abstract = paper.get('summary', '')  # Fallback to summary if abstract is not available
                
                # Get additional metadata with fallbacks
                authors = ', '.join(paper.get('authors', ['Unknown Author']))
                categories = ', '.join(paper.get('categories', ['Uncategorized']))
                
                # Get content if available
                content = paper.get('content', '')
                if content:
                    paper_details.append(
                        f"Title: {title}\n"
                        f"Authors: {authors}\n"
                        f"Categories: {categories}\n"
                        f"Abstract: {abstract}\n"
                        f"Content: {content[:1000]}...\n"  # Limit content length
                    )
                else:
                    paper_details.append(
                        f"Title: {title}\n"
                        f"Authors: {authors}\n"
                        f"Categories: {categories}\n"
                        f"Abstract: {abstract}\n"
                    )
            except Exception as e:
                print(f"Error processing paper {paper.get('title', 'Unknown')}: {str(e)}")
                continue

        if not paper_details:
            return "No valid paper content available for summarization."

        # Constructing a prompt for summarizing the papers
        prompt = (
            "Please provide a comprehensive summary of the following research papers. "
            "Focus on the key findings, methodologies, and their relationships. "
            "Structure your response with:\n"
            "1. Overall theme and significance\n"
            "2. Key findings from each paper\n"
            "3. Common methodologies and approaches\n"
            "4. Future directions and implications\n\n"
            f"{'='*50}\n".join(paper_details)
        )

        # Query Ollama for summarization
        summary = query_ollama(prompt)
        
        if not summary:
            return "Unable to generate summary. Please try again."
            
        return summary

    except Exception as e:
        print(f"Error in paper summarization: {str(e)}")
        return "Error generating summary. Please try again."

