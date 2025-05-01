from fastapi import FastAPI, Query
from ArXiv_utils import search_arxiv

app = FastAPI()

@app.get("/search")
def search_papers(query: str = Query(..., description="Search term for ArXiv")):
    results = search_arxiv(query)
    return {"results": results}
