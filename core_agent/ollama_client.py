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
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"].strip()


def extract_keywords(text: str) -> list[str]:
    prompt = (
        f"EXTRACT 5 to 7 Keywords(field of study) from input in the brackets "
        f"that can be used to search for research papers:<\n\n\"{text}\"\n\n>"
        "Return only a comma-separated list of keywords. "
        "no need state that these are keywords."
        "Do not include any explanations, numbers, or extra text. "
        "fill in the spaces between individual keywords with an underscore."
        "Only output the keywords, separated by commas."

    )
    response = query_ollama(prompt)
    # Post-process: Remove any lines that are not comma-separated keywords
    # (in case the model still adds extra text)
    # Only keep the first line with commas
    for line in response.splitlines():
        if ',' in line:
            return [kw.strip() for kw in line.split(',')]
    # Fallback: split the whole response
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

