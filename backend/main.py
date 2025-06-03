from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import List, Optional
from models.paper import Paper, PaperCreate, PaperUpdate
from models.chat import Chat, ChatCreate, ChatUpdate, Message, Cluster, ClusterCreate, ClusterUpdate
from models.search import SearchQuery  # Import the new model
from utils.paper_service import paper_service
from utils.chat_service import chat_service, cluster_service
from utils.memory_service import memory_service
from utils.embedding_service import embedding_service
from utils.paper_search_service import paper_search_service
from utils.ollama_interface import get_ollama_client
from utils.arxiv_service import arxiv_service

app = FastAPI(
    title="Research Companion API",
    description="API for exploring and analyzing research papers with AI assistance",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Test Ollama connection
        client = get_ollama_client()
        await client.chat("llama2", [{"role": "user", "content": "test"}])
    except Exception as e:
        print(f"Warning: Could not connect to Ollama: {str(e)}")
        print("Please ensure Ollama is running on http://localhost:11434")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    try:
        client = get_ollama_client()
        await client.close()
    except Exception as e:
        print(f"Warning: Error during shutdown: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Research Companion API"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy"},
        status_code=200
    )

# New endpoint for initial paper search
@app.post("/api/search")
async def search_papers(search_query: SearchQuery):  # Accept SearchQuery model
    """Search for papers on arXiv and process them."""
    query = search_query.query # Extract query from the model
    try:
        # Search arXiv for papers
        papers = await arxiv_service.search_papers(query)
        
        # Process each paper
        processed_papers = []
        for paper in papers:
            # Create paper in database
            paper_create = PaperCreate(
                title=paper['title'],
                authors=paper['authors'],
                content=paper['abstract'],  # Using abstract as content for now
                metadata={
                    'year': paper['year'],
                    'abstract': paper['abstract'],
                    'citations': paper['citations'],
                    'keywords': paper['keywords'],
                    'url': paper['url'],
                    'pdf_url': paper['pdf_url']
                }
            )
            stored_paper = paper_service.create_paper(paper_create)
            
            # Process paper for embeddings
            chunks = paper_service.split_into_chunks(stored_paper.content)
            chunk_embeddings = []
            for chunk in chunks:
                embedding = await embedding_service.get_embedding(chunk['text'])
                chunk['embedding'] = embedding
                chunk_embeddings.append(chunk)
            await memory_service.store_paper_chunks(stored_paper.id, chunk_embeddings)
            
            processed_papers.append(stored_paper)
        
        return {
            'query': query,
            'papers': processed_papers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Paper endpoints
@app.get("/api/papers", response_model=List[Paper])
async def get_papers():
    return paper_service.get_all_papers()

@app.get("/api/papers/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    paper = paper_service.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@app.post("/api/papers", response_model=Paper)
async def create_paper(paper: PaperCreate):
    return paper_service.create_paper(paper)

@app.put("/api/papers/{paper_id}", response_model=Paper)
async def update_paper(paper_id: str, paper_update: PaperUpdate):
    paper = paper_service.update_paper(paper_id, paper_update)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@app.delete("/api/papers/{paper_id}")
async def delete_paper(paper_id: str):
    if not paper_service.delete_paper(paper_id):
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"message": "Paper deleted successfully"}

@app.get("/api/papers/search/{query}", response_model=List[Paper])
async def search_papers(query: str):
    return paper_service.search_papers(query)

# Chat endpoints
@app.get("/api/chats", response_model=List[Chat])
async def get_chats():
    return chat_service.get_all_chats()

@app.get("/api/chats/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str):
    chat = chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.post("/api/chats", response_model=Chat)
async def create_chat(chat: ChatCreate):
    return chat_service.create_chat(chat)

@app.put("/api/chats/{chat_id}", response_model=Chat)
async def update_chat(chat_id: str, chat_update: ChatUpdate):
    chat = chat_service.update_chat(chat_id, chat_update)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    if not chat_service.delete_chat(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat deleted successfully"}

@app.post("/api/chats/{chat_id}/messages", response_model=Message)
async def add_message(chat_id: str, content: str, paper_id: Optional[str] = None):
    message = chat_service.add_message(chat_id, content, paper_id)
    if not message:
        raise HTTPException(status_code=404, detail="Chat not found")
    return message

# Cluster endpoints
@app.get("/api/clusters", response_model=List[Cluster])
async def get_clusters():
    return cluster_service.get_all_clusters()

@app.get("/api/clusters/{cluster_id}", response_model=Cluster)
async def get_cluster(cluster_id: str):
    cluster = cluster_service.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@app.post("/api/clusters", response_model=Cluster)
async def create_cluster(cluster: ClusterCreate):
    return cluster_service.create_cluster(cluster)

@app.put("/api/clusters/{cluster_id}", response_model=Cluster)
async def update_cluster(cluster_id: str, cluster_update: ClusterUpdate):
    cluster = cluster_service.update_cluster(cluster_id, cluster_update)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@app.delete("/api/clusters/{cluster_id}")
async def delete_cluster(cluster_id: str):
    if not cluster_service.delete_cluster(cluster_id):
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"message": "Cluster deleted successfully"}

# New endpoints for context-aware Q&A
@app.post("/api/papers/{paper_id}/ask")
async def ask_question(paper_id: str, question: str):
    """Ask a question about a paper and get a context-aware answer."""
    try:
        result = await chat_service.process_question(paper_id, question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/papers/{paper_id}/chat-history")
async def get_paper_chat_history(paper_id: str):
    """Get chat history for a paper."""
    try:
        history = await chat_service.get_chat_history(paper_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/papers/{paper_id}/clusters")
async def get_paper_clusters(paper_id: str):
    """Get clusters for a paper's Q&A pairs."""
    try:
        clusters = await chat_service.get_clusters(paper_id)
        return clusters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Paper processing endpoints
@app.post("/api/papers/{paper_id}/process")
async def process_paper(paper_id: str):
    """Process a paper and store its chunks with embeddings."""
    try:
        paper = paper_service.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Get paper content and split into chunks
        chunks = paper_service.split_into_chunks(paper.content)
        
        # Get embeddings for chunks
        chunk_embeddings = []
        for chunk in chunks:
            embedding = await embedding_service.get_embedding(chunk['text'])
            chunk['embedding'] = embedding
            chunk_embeddings.append(chunk)
        
        # Store chunks
        await memory_service.store_paper_chunks(paper_id, chunk_embeddings)
        
        return {"message": "Paper processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research")
async def research_topic(query: str):
    """Handle an initial research question and return relevant papers."""
    try:
        # Search for relevant papers
        papers = await paper_search_service.search_papers(query)
        
        # Process each paper to generate embeddings
        for paper in papers:
            paper_id = paper['id']
            content = paper_search_service.get_paper_content(paper_id)
            
            # Store paper in the database
            paper_create = PaperCreate(
                title=paper['title'],
                authors=paper['authors'],
                content=content,
                metadata={
                    'year': paper['year'],
                    'abstract': paper['abstract'],
                    'citations': paper['citations'],
                    'keywords': paper['keywords']
                }
            )
            stored_paper = paper_service.create_paper(paper_create)
            
            # Process paper for embeddings
            chunks = paper_service.split_into_chunks(stored_paper.content)
            chunk_embeddings = []
            for chunk in chunks:
                embedding = await embedding_service.get_embedding(chunk['text'])
                chunk['embedding'] = embedding
                chunk_embeddings.append(chunk)
            await memory_service.store_paper_chunks(stored_paper.id, chunk_embeddings)
        
        return {
            'query': query,
            'papers': papers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 