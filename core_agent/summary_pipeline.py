# Keyword extraction, ArXiv search and summarization
from core_agent.utils.arxiv_api import search_arxiv
from core_agent.ollama_client import extract_keywords, summarize_papers
from core_agent.ollama_client import query_ollama

def extract_keywords(user_input: str) -> list[str]:
    prompt = (
        f"Extract 5 to 7 important keywords from the following user query "
        f"that can be used to search for research papers:\n\n\"{user_input}\"\n\n"
        "Return only a comma-separated list of keywords."
    )
    response = query_ollama(prompt)
    return [kw.strip() for kw in response.split(',')]

def summarize_topic(user_input: str) -> dict:
    # Step 1: Extract keywords using LLM
    keywords = extract_keywords(user_input)

    # Step 2: Use keywords to search ArXiv
    papers = search_arxiv(keywords)

    #.Summarize top papers
    summary = summarize_papers(papers)

    return {
        "keywords": keywords,
        "papers": papers,
        "summary": summary
    }