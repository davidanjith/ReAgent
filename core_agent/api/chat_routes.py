"""
FastAPI routes for paper chat functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..paper_chat import PaperChat

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize the chat system
chat_system = PaperChat()

class ChatRequest(BaseModel):
    question: str
    multi_doc: bool = False

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

@router.post("/papers", response_model=ChatResponse)
async def chat_with_papers(request: ChatRequest):
    """
    Chat with papers by retrieving relevant documents and generating a response.
    
    Args:
        request (ChatRequest): The chat request containing the question and mode
        
    Returns:
        ChatResponse: The generated response or error message
    """
    try:
        response = chat_system.chat_with_papers(
            question=request.question,
            multi_doc=request.multi_doc
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        ) 