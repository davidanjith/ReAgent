from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from core_agent.paper_search import PaperSearch
from core_agent.chat_engine import ChatEngine
from core_agent.pdf_parser import PDFParser
import traceback
import logging
import asyncio
import json
from datetime import datetime
import time
from PyPDF2 import PdfReader
import io
from core_agent.summary_pipeline import summarize_topic

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
pdf_parser = PDFParser()

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""
    paper_id: Optional[str] = None

class SummarizeRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class HighlightRequest(BaseModel):
    text: str
    paper_id: str

@app.post("/search/")
async def search_papers(request: SearchRequest):
    start_time = time.time()
    try:
        logger.info(f"Starting search pipeline for query: {request.query}")
        
        # Use summarize_topic to handle the entire pipeline
        result = summarize_topic(request.query, max_papers=request.max_results)
        
        if "error" in result:
            return {
                "metadata": {
                    "query": request.query,
                    "total_papers": 0,
                    "timestamp": datetime.now().isoformat(),
                    "processing_time": time.time() - start_time
                },
                "papers": [],
                "summary": result["error"],
                "knowledge_graph": {"nodes": [], "edges": []}
            }
        
        # Return the complete result
        return {
            "metadata": {
                "query": request.query,
                "total_papers": len(result["papers"]),
                "timestamp": datetime.now().isoformat(),
                "processing_time": time.time() - start_time
            },
            "papers": result["papers"],
            "summary": result["summary"],
            "knowledge_graph": {"nodes": result["keywords"], "edges": []}
        }
            
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

@app.post("/summarize/")
async def summarize_papers(request: SummarizeRequest):
    try:
        logger.info(f"Received summarize request for query: {request.query}")
        
        # Use the summarize_topic function from summary_pipeline
        result = summarize_topic(request.query, max_papers=request.max_results)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return {
            "papers": result["papers"],
            "summary": result["summary"],
            "keywords": result["keywords"]
        }
            
    except Exception as e:
        logger.error(f"Error in summarize_papers: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to ReAgent API!"}
