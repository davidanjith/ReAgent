import feedparser

def search_arxiv(query, max_results=5):
    base_url = "http://export.arxiv.org/api/query"
    full_url = f"{base_url}?search_query=all:{query}&start=0&max_results={max_results}"
    feed = feedparser.parse(full_url)

    papers = []
    for entry in feed.entries:
        papers.append({
            "title": entry.title,
            "authors": [author.name for author in entry.authors],
            "summary": entry.summary,
            "pdf_url": next((link.href for link in entry.links if link.type == 'application/pdf'), None),
            "published": entry.published
        })

    return papers
