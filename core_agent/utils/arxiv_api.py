# core_agent/utils/arxiv_api.py

import requests
import xml.etree.ElementTree as ET
import logging
import time
import re

logger = logging.getLogger(__name__)
ARXIV_API = "https://export.arxiv.org/api/query"

def _extract_version(paper_id: str) -> str:
    """Extract version number from paper ID."""
    match = re.search(r'v(\d+)$', paper_id)
    return match.group(1) if match else '1'

def _construct_pdf_url(paper_id: str) -> str:
    """Construct the correct PDF URL for an arXiv paper."""
    try:
        # Remove version number if present
        base_id = re.sub(r'v\d+$', '', paper_id)
        
        # Handle old paper IDs (before 2007)
        if len(base_id) <= 7:  # Old format (e.g., 9510005)
            # Extract year and number
            year = base_id[:2]
            number = base_id[2:]
            return f"https://arxiv.org/pdf/{year}/{number}.pdf"
        elif '.' in base_id:  # New format (e.g., 1712.04669)
            # Add version number
            version = _extract_version(paper_id)
            return f"https://arxiv.org/pdf/{base_id}v{version}.pdf"
        else:  # Fallback format
            return f"https://arxiv.org/pdf/{paper_id}.pdf"
    except Exception as e:
        logger.error(f"Error constructing PDF URL for {paper_id}: {str(e)}")
        return f"https://arxiv.org/pdf/{paper_id}.pdf"  # Fallback URL

def search_arxiv(keywords: list[str], max_results=5) -> list[dict]:
    if not keywords:
        logger.warning("No keywords provided for arXiv search")
        return []
        
    # Clean and prepare keywords
    cleaned_keywords = [kw.strip().replace("_", " ") for kw in keywords if kw.strip()]
    if not cleaned_keywords:
        logger.warning("No valid keywords after cleaning")
        return []
        
    # Construct query - removed quotes around keywords
    query = '+OR+'.join(f'all:{kw}' for kw in cleaned_keywords[:3])
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }

    try:
        # Construct full URL for logging
        full_url = f"{ARXIV_API}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        logger.info(f"Searching arXiv with URL: {full_url}")
        
        # Add delay to respect API rate limits
        time.sleep(3)
        
        response = requests.get(ARXIV_API, params=params)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}

        results = []
        for entry in root.findall('atom:entry', ns):
            try:
                # Get the paper ID from the atom:id field
                entry_id = entry.find('atom:id', ns).text.strip()
                paper_id = entry_id.split('/')[-1]
                
                # Get abstract/summary
                summary_elem = entry.find('atom:summary', ns)
                summary = summary_elem.text.strip() if summary_elem is not None else ""
                
                # Get categories
                categories = [cat.get('term') for cat in entry.findall('arxiv:primary_category', ns) + 
                            entry.findall('atom:category', ns)]
                
                # Construct PDF URL
                pdf_url = _construct_pdf_url(paper_id)
                
                result = {
                    'title': entry.find('atom:title', ns).text.strip(),
                    'summary': summary,
                    'authors': [author.find('atom:name', ns).text.strip() 
                              for author in entry.findall('atom:author', ns)],
                    'published': entry.find('atom:published', ns).text.strip(),
                    'entry_id': entry_id,
                    'paper_id': paper_id,
                    'pdf_url': pdf_url,
                    'categories': categories
                }
                results.append(result)
                logger.debug(f"Added paper: {result['title']}")
            except (AttributeError, TypeError) as e:
                logger.error(f"Error parsing paper entry: {str(e)}")
                continue

        logger.info(f"Found {len(results)} papers")
        return results

    except requests.RequestException as e:
        logger.error(f"Error making arXiv API request: {str(e)}")
        return []
    except ET.ParseError as e:
        logger.error(f"Error parsing arXiv API response: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in arXiv search: {str(e)}")
        return []