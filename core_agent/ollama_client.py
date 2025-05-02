# Handles interaction with Ollama (LLM backend)

import requests

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "llama3"  # Or whichever model you loaded

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
    # TODO: Replace with real LLM summarization
    return "Summary of the top relevant papers goes here."
