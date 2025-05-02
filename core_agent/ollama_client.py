# Handles interaction with Ollama (LLM backend)

import requests
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

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
    # TODO: Replace with real Ollama inference
    return text.lower().split()[:5]  # dummy keyword extraction


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
