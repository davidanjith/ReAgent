from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from core_agent.paper_search import PaperSearch
from core_agent.chat_engine import ChatEngine

# Configure logging
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

# Initialize components
paper_search = PaperSearch()
chat_engine = ChatEngine()

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

class ChatRequest(BaseModel):
    message: str
    paper_id: Optional[str] = None
    context: Optional[str] = ""

class HighlightRequest(BaseModel):
    text: str
    paper_id: str

class PaperChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""

@app.post("/search/")
async def search_papers(request: SearchRequest):
    try:
        logger.info(f"Received search request for query: {request.query}")
        papers = await paper_search.search(request.query, request.max_results)
        logger.info(f"Found {len(papers)} papers")
        return {"papers": papers}
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.message}")
        response = await chat_engine.chat(
            message=request.message,
            context=request.context,
            paper_id=request.paper_id
        )
        return response
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        logger.error(f"Traceback: {e.__traceback__}")
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
        logger.error(f"Traceback: {e.__traceback__}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/paper/{paper_id}")
async def get_paper_details(paper_id: str):
    try:
        logger.info(f"Getting details for paper: {paper_id}")
        paper_details = await paper_search.get_paper_details(paper_id)
        return paper_details
    except Exception as e:
        logger.error(f"Error in get_paper_details: {str(e)}")
        logger.error(f"Traceback: {e.__traceback__}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/paper/{paper_id}/full-text")
async def get_paper_full_text(paper_id: str):
    try:
        logger.info(f"Getting full text for paper: {paper_id}")
        text = await paper_search.get_full_text(paper_id)
        if text is None:
            raise HTTPException(status_code=404, detail="Paper not found")
        return {"text": text}
    except Exception as e:
        logger.error(f"Error in get_paper_full_text: {str(e)}")
        logger.error(f"Traceback: {e.__traceback__}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge-graph/")
async def get_knowledge_graph():
    try:
        return chat_engine.get_knowledge_graph()
    except Exception as e:
        logger.error(f"Error getting knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/paper/{paper_id}/chat")
async def chat_about_paper(paper_id: str, req: PaperChatRequest):
    try:
        logger.info(f"[CHAT] paper_id={paper_id}, message={req.message}")
        response = await paper_search.chat_about_paper(paper_id, req.message)
        if not response or 'response' not in response:
            logger.error(f"[CHAT] No response from chat_about_paper for paper_id={paper_id}")
            raise HTTPException(status_code=500, detail="No response from chat engine.")
        return {"response": response["response"]}
    except Exception as e:
        logger.error(f"[CHAT] Exception for paper_id={paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to ReAgent API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
