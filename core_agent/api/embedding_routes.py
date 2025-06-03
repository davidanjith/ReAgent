"""
FastAPI routes for document embedding and storage.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..embedding.embedding_pipeline import embed_and_store, batch_embed_and_store, EmbeddingError

router = APIRouter(prefix="/embed", tags=["embedding"])

class DocumentRequest(BaseModel):
    text: str
    metadata: Dict[str, Any]

class BatchDocumentRequest(BaseModel):
    texts: List[str]
    metadata_list: List[Dict[str, Any]]

class DocumentResponse(BaseModel):
    doc_id: str

class BatchDocumentResponse(BaseModel):
    doc_ids: List[Optional[str]]

@router.post("/document", response_model=DocumentResponse)
async def embed_document(request: DocumentRequest):
    """
    Embed and store a single document.
    """
    try:
        doc_id = embed_and_store(request.text, request.metadata)
        return DocumentResponse(doc_id=doc_id)
    except EmbeddingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/documents", response_model=BatchDocumentResponse)
async def embed_documents(request: BatchDocumentRequest):
    """
    Embed and store multiple documents in batch.
    """
    try:
        doc_ids = batch_embed_and_store(request.texts, request.metadata_list)
        return BatchDocumentResponse(doc_ids=doc_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 