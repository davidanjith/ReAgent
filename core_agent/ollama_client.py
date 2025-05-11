import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API = os.getenv("OLLAMA_URL")
MODEL = os.getenv("OLLAMA_MODEL")


def query_ollama(prompt: str) -> str:
    response = requests.post(OLLAMA_API, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"].strip()


def extract_keywords(text: str) -> list[str]:
    prompt = (
        f"Extract 5 to 7 concise academic research keywords (fields of study) "
        f"from the following input:\n\n\"{text}\"\n\n"
        "Output a single comma-separated list of keywords.\n"
        "Use underscores **within** multi-word keywords only (e.g., 'computer_science').\n"
        "Do not include explanations, numbers, or extra text.\n"
        "Just output the keywords, separated by commas."
    )

    response = query_ollama(prompt)

    # Post-process to extract the first valid line with comma-separated values
    for line in response.splitlines():
        if ',' in line:
            return [kw.strip() for kw in line.split(',')]

    return [kw.strip() for kw in response.split(',')]


def summarize_papers(papers: list[dict]) -> str:
    # Collecting the titles and summaries of the papers to create a prompt for summarization
    paper_details = "\n\n".join([
        f"Title: {paper['title']}\nSummary: {paper['summary']}"
        for paper in papers
    ])

    # Constructing a prompt for summarizing the papers
    prompt = f"Summarize the following research papers:\n\n{paper_details}"

    # Query Ollama for summarization
    summary = query_ollama(prompt)

    # Returning the summarized content
    return summary

