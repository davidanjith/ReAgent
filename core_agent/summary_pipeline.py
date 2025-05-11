# Keyword extraction, ArXiv search and summarization
from core_agent.utils.arxiv_api import search_arxiv
from core_agent.ollama_client import extract_keywords, summarize_papers

def summarize_topic(user_input: str) -> dict:
    """
    Full summarization pipeline:
    1. Extract keywords from user input using LLM (Ollama).
    2. Query ArXiv API with those keywords.
    3. Summarize top papers via LLM.
    4. Return the keywords, original papers, and their summaries.
    """
    keywords = extract_keywords(user_input)

    papers = search_arxiv(keywords)

    summary = summarize_papers(papers)

    # Step 4: Return combined result
    return {
        "keywords": keywords,
        "papers": papers,
        "summary": summary
    }