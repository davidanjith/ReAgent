from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from core_agent.paper_search import PaperSearch
from core_agent.chat_engine import ChatEngine
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our services
paper_search = PaperSearch()
chat_engine = ChatEngine()

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""
    paper_id: Optional[str] = None

class HighlightRequest(BaseModel):
    text: str
    paper_id: str

@app.post("/search/")
async def search_papers(request: SearchRequest):
    try:
        logger.info(f"Received search request for query: {request.query}")
        papers = await paper_search.search_papers(request.query, request.max_results)
        logger.info(f"Found {len(papers)} papers")
        return {"papers": papers}
    except Exception as e:
        logger.error(f"Error in search_papers: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.message}")
        # If paper_id is provided, get paper context
        context = request.context
        if request.paper_id:
            paper_details = await paper_search.get_paper_details(request.paper_id)
            context = f"Paper: {paper_details['title']}\nAbstract: {paper_details['abstract']}\n\n{context}"
        
        response = await chat_engine.chat(request.message, context)
        return response
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/highlight/")
async def process_highlight(request: HighlightRequest):
    try:
        logger.info(f"Received highlight request for paper: {request.paper_id}")
        # Get paper details for context
        paper_details = await paper_search.get_paper_details(request.paper_id)
        context = f"Paper: {paper_details['title']}\nHighlighted text: {request.text}"
        
        # Process the highlight through the chat engine
        response = await chat_engine.chat("Please analyze this highlighted text and extract key concepts.", context)
        return response
    except Exception as e:
        logger.error(f"Error in process_highlight: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge-graph/")
async def get_knowledge_graph():
    try:
        return chat_engine.get_knowledge_graph()
    except Exception as e:
        logger.error(f"Error in get_knowledge_graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to ReAgent API!"}
