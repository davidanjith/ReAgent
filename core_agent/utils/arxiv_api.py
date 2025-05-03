# core_agent/utils/arxiv_api.py

import requests
import xml.etree.ElementTree as ET

ARXIV_API = "https://export.arxiv.org/api/query"

def search_arxiv(keywords: list[str], max_results=5) -> list[dict]:
    query = '+AND+'.join(f'all:{kw}' for kw in keywords)
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }

    response = requests.get(ARXIV_API, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    results = []
    for entry in root.findall('atom:entry', ns):
        result = {
            'title': entry.find('atom:title', ns).text.strip(),
            'summary': entry.find('atom:summary', ns).text.strip(),
            'authors': [author.find('atom:name', ns).text.strip() for author in entry.findall('atom:author', ns)],
            'published': entry.find('atom:published', ns).text.strip(),
            'link': entry.find('atom:id', ns).text.strip(),
        }
        results.append(result)

    return results
