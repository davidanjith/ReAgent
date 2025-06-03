from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from core_agent.paper_search import PaperSearch
from core_agent.pdf_parser import PDFParser
from core_agent.embedding.ollama_embedder import OllamaEmbedder
from core_agent.vector_store.redis_store import RedisVectorStore
import traceback
import logging
import sys
from datetime import datetime
import time
from core_agent.summary_pipeline import summarize_topic
import json
import requests

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

try:
    embedder = OllamaEmbedder()
    vector_store = RedisVectorStore()
    logger.info("Embedding and vector store services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize embedding services: {str(e)}")
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

class EmbedPaperRequest(BaseModel):
    paper_id: str

class ChatRequest(BaseModel):
    message: str
    paper_id: str
    max_context_chunks: Optional[int] = 10

class ChatResponse(BaseModel):
    response: str
    context: List[Dict[str, Any]]
    metadata: Dict[str, Any]

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

@app.post("/embed-paper/")
async def embed_paper(request: EmbedPaperRequest):
    request_id = f"embed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"[{request_id}] Starting paper embedding for paper_id: {request.paper_id}")
    
    try:
        # Load the parsed paper JSON
        parsed_path = pdf_parser.parsed_dir / f"{request.paper_id}_parsed.json"
        if not parsed_path.exists():
            raise HTTPException(status_code=404, detail=f"No parsed paper found for ID: {request.paper_id}")
        
        logger.info(f"[{request_id}] Loading parsed paper from {parsed_path}")
        with open(parsed_path, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
        
        # Create embeddings for each section
        sections = paper_data.get("sections", {})
        logger.info(f"[{request_id}] Found {len(sections)} sections to embed")
        
        section_embeddings = {}
        for section_name, section_text in sections.items():
            logger.info(f"[{request_id}] Embedding section: {section_name}")
            logger.info(f"[{request_id}] Section text length: {len(section_text)}")
            
            # Truncate text if too long (some models have token limits)
            if len(section_text) > 10000:
                section_text = section_text[:10000]
                logger.info(f"[{request_id}] Truncated section text to 10000 characters")
            
            embedding = embedder.get_embedding(section_text)
            if embedding:
                logger.info(f"[{request_id}] Successfully generated embedding for section {section_name} with dimension {len(embedding)}")
                # Store in vector store
                doc_id = vector_store.store_document(
                    text=section_text,
                    embedding=embedding,
                    metadata={
                        "paper_id": request.paper_id,
                        "section": section_name,
                        "title": paper_data.get("title", ""),
                        "authors": paper_data.get("authors", [])
                    }
                )
                section_embeddings[section_name] = doc_id
                logger.info(f"[{request_id}] Stored section {section_name} with doc_id: {doc_id}")
            else:
                logger.error(f"[{request_id}] Failed to generate embedding for section {section_name}")
        
        if not section_embeddings:
            logger.error(f"[{request_id}] No sections were successfully embedded")
            raise HTTPException(status_code=500, detail="Failed to generate embeddings for any sections")
        
        logger.info(f"[{request_id}] Successfully embedded {len(section_embeddings)} sections")
        
        # Verify embeddings were stored
        all_keys = vector_store.vector_client.keys("embedding:*")
        logger.info(f"[{request_id}] Found {len(all_keys)} total embeddings in Redis")
        
        return {
            "paper_id": request.paper_id,
            "title": paper_data.get("title", ""),
            "sections_embedded": list(section_embeddings.keys()),
            "section_ids": section_embeddings,
            "total_embeddings": len(all_keys)
        }
            
    except Exception as e:
        logger.error(f"[{request_id}] Error in embed_paper: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/", response_model=ChatResponse)
async def chat_with_paper(request: ChatRequest):
    request_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"[{request_id}] Starting chat for paper_id: {request.paper_id}")
    
    try:
        # Get embedding for the user's message
        message_embedding = embedder.get_embedding(request.message)
        if not message_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate message embedding")
        
        logger.info(f"[{request_id}] Generated message embedding with dimension: {len(message_embedding)}")
        
        # Search for relevant context
        similar_docs = vector_store.search_similar(
            query_embedding=message_embedding,
            paper_id=request.paper_id,
            top_k=request.max_context_chunks
        )
        
        logger.info(f"[{request_id}] Found {len(similar_docs)} similar documents")
        
        # Prepare context for the LLM
        context = []
        for doc in similar_docs:
            context.append({
                "text": doc["text"],
                "section": doc["metadata"].get("section", "Unknown"),
                "relevance_score": doc["score"]
            })
            logger.info(f"[{request_id}] Added section {doc['metadata'].get('section', 'Unknown')} with score {doc['score']}")
        
        logger.info(f"[{request_id}] Found {len(context)} relevant sections from paper {request.paper_id}")
        
        if not context:
            # If no context found, try to load the entire paper as fallback
            logger.info(f"[{request_id}] No relevant sections found, attempting to load entire paper as fallback")
            try:
                # Load the parsed paper JSON
                parsed_path = pdf_parser.parsed_dir / f"{request.paper_id}_parsed.json"
                if parsed_path.exists():
                    with open(parsed_path, 'r', encoding='utf-8') as f:
                        paper_data = json.load(f)
                    
                    # Format the entire paper content
                    full_context = []
                    for section_name, section_text in paper_data.get("sections", {}).items():
                        full_context.append({
                            "text": section_text,
                            "section": section_name,
                            "relevance_score": 1.0  # Full relevance since we're using everything
                        })
                    
                    if full_context:
                        logger.info(f"[{request_id}] Successfully loaded entire paper as fallback")
                        context = full_context
                    else:
                        logger.warning(f"[{request_id}] Paper exists but has no sections")
                else:
                    logger.warning(f"[{request_id}] Paper {request.paper_id} not found in parsed directory")
            except Exception as e:
                logger.error(f"[{request_id}] Error loading paper as fallback: {str(e)}")
        
        if not context:
            return ChatResponse(
                response="I couldn't find any information about this paper. Please make sure the paper has been embedded first using the /embed-paper/ endpoint.",
                context=[],
                metadata={
                    "paper_id": request.paper_id,
                    "timestamp": datetime.now().isoformat(),
                    "context_sections": [],
                    "error": "Paper not found"
                }
            )
        
        # Format context into a prompt
        context_text = "\n\n".join([
            f"Section: {c['section']}\nRelevance Score: {c['relevance_score']:.2f}\nContent: {c['text']}"
            for c in context
        ])
        
        # Adjust prompt based on whether we're using RAG or fallback
        if len(context) > request.max_context_chunks:
            prompt = f"""You are a helpful research assistant. I'm providing you with the entire paper content to answer the user's question.
Please analyze the paper and provide a comprehensive answer.

Paper content:
{context_text}

User's question: {request.message}

Please provide a detailed answer based on the paper's content:"""
        else:
            prompt = f"""You are a helpful research assistant. Use the following context from a research paper to answer the user's question.
If the context doesn't contain enough information to answer the question, say so.

Context from the paper:
{context_text}

User's question: {request.message}

Please provide a detailed answer based on the paper's content:"""
        
        # Get response from Ollama
        try:
            logger.info(f"[{request_id}] Sending request to Ollama API")
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3:latest",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                },
                timeout=30  # Add timeout
            )
            
            if response.status_code != 200:
                logger.error(f"[{request_id}] Ollama API returned status code {response.status_code}")
                logger.error(f"[{request_id}] Response content: {response.text}")
                raise Exception(f"Ollama API returned status code {response.status_code}")
            
            response_data = response.json()
            if "response" not in response_data:
                logger.error(f"[{request_id}] Unexpected Ollama API response format: {response_data}")
                raise Exception("Unexpected Ollama API response format")
            
            llm_response = response_data["response"].strip()
            logger.info(f"[{request_id}] Successfully received response from Ollama API")
            
        except requests.exceptions.Timeout:
            logger.error(f"[{request_id}] Ollama API request timed out")
            llm_response = "I apologize, but the request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            logger.error(f"[{request_id}] Failed to connect to Ollama API")
            llm_response = "I apologize, but I couldn't connect to the language model. Please make sure Ollama is running."
        except Exception as e:
            logger.error(f"[{request_id}] Error getting response from Ollama: {str(e)}")
            llm_response = "I apologize, but I encountered an error while trying to generate a response. Please try again."
        
        return ChatResponse(
            response=llm_response,
            context=context,
            metadata={
                "paper_id": request.paper_id,
                "timestamp": datetime.now().isoformat(),
                "context_sections": [c["section"] for c in context],
                "relevance_scores": [c["relevance_score"] for c in context],
                "used_fallback": len(context) > request.max_context_chunks
            }
        )
            
    except Exception as e:
        logger.error(f"[{request_id}] Error in chat_with_paper: {str(e)}")
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
