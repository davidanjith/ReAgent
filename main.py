from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from core_agent.paper_search import PaperSearch
from core_agent.pdf_parser import PDFParser
import traceback
import logging
import sys
from datetime import datetime
import time
from core_agent.summary_pipeline import summarize_topic

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create console handler with formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# Remove any existing handlers and add our console handler
root_logger.handlers = []
root_logger.addHandler(console_handler)

# Create a logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add a startup log message
logger.info("Starting ReAgent API server...")

app = FastAPI(
    title="ReAgent API",
    description="API for paper analysis and chat functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our services with logging
logger.info("Initializing services...")
try:
    paper_search = PaperSearch()
    logger.info("PaperSearch service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PaperSearch: {str(e)}")
    raise

try:
    pdf_parser = PDFParser()
    logger.info("PDFParser service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PDFParser: {str(e)}")
    raise

# Include the routers with logging
logger.info("Including API routers...")
logger.info("API routers included successfully")

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class SummarizeRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class HighlightRequest(BaseModel):
    text: str
    paper_id: str

@app.post("/search/")
async def search_papers(request: SearchRequest):
    start_time = time.time()
    request_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"[{request_id}] Starting search pipeline for query: {request.query}")
    logger.info(f"[{request_id}] Request body: {request.dict()}")
    
    try:
        # Use summarize_topic to handle the entire pipeline
        logger.info(f"[{request_id}] Calling summarize_topic with query: {request.query}, max_papers: {request.max_results}")
        
        # Log each step of the pipeline
        logger.info(f"[{request_id}] Step 1: Extracting keywords...")
        result = summarize_topic(request.query, max_papers=request.max_results)
        logger.info(f"[{request_id}] Keywords extracted: {result.get('keywords', [])}")
        
        if "error" in result:
            logger.error(f"[{request_id}] Search pipeline failed: {result['error']}")
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
        
        logger.info(f"[{request_id}] Step 2: Processing papers...")
        logger.info(f"[{request_id}] Found {len(result['papers'])} papers")
        
        # Ensure each paper has the correct PDF URL
        for paper in result['papers']:
            if 'pdf_url' not in paper and 'url' in paper:
                paper['pdf_url'] = paper['url']
            elif 'pdf_url' not in paper and 'entry_id' in paper:
                # Construct arXiv PDF URL from entry_id
                paper_id = paper['entry_id'].split('/')[-1]
                paper['pdf_url'] = f"https://arxiv.org/pdf/{paper_id}.pdf"
        
        logger.info(f"[{request_id}] Step 3: Generating summary...")
        logger.info(f"[{request_id}] Summary generated successfully")
        
        processing_time = time.time() - start_time
        logger.info(f"[{request_id}] Search completed successfully in {processing_time:.2f}s. Found {len(result['papers'])} papers.")
        
        # Log papers data before returning to check structure and IDs
        logger.info(f"[{request_id}] Returning papers data. Number of papers: {len(result['papers'])}")
        for i, paper in enumerate(result['papers']):
            logger.info(f"[{request_id}] Paper {i} data: {paper}")

        # Return the complete result
        return {
            "metadata": {
                "query": request.query,
                "total_papers": len(result["papers"]),
                "timestamp": datetime.now().isoformat(),
                "processing_time": processing_time
            },
            "papers": result["papers"],
            "summary": result["summary"],
            "knowledge_graph": {"nodes": result["keywords"], "edges": []}
        }
            
    except Exception as e:
        logger.error(f"[{request_id}] Error in search_papers: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize/")
async def summarize_papers(request: SummarizeRequest):
    request_id = f"summarize_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"[{request_id}] Received summarize request for query: {request.query}")
    
    try:
        # Use the summarize_topic function from summary_pipeline
        result = summarize_topic(request.query, max_papers=request.max_results)
        
        if "error" in result:
            logger.error(f"[{request_id}] Summarization failed: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"[{request_id}] Summarization completed successfully")
        return {
            "papers": result["papers"],
            "summary": result["summary"],
            "keywords": result["keywords"]
        }
            
    except Exception as e:
        logger.error(f"[{request_id}] Error in summarize_papers: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to ReAgent API!"}

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    logger.info("ReAgent API server is starting up...")

# Add shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ReAgent API server is shutting down...")
