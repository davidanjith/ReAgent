from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from ..utils.paper_processor import PaperProcessor
from ..utils.embedding_clustering import EmbeddingClustering
from ..ollama_interface import OllamaInterface
import json

router = APIRouter()
paper_processor = PaperProcessor()
embedding_clustering = EmbeddingClustering()
ollama = OllamaInterface()

@router.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    """Upload and process a research paper."""
    try:
        # Save the uploaded file temporarily
        contents = await file.read()
        temp_path = paper_processor.temp_dir / file.filename
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Process the paper
        result = await paper_processor.process_paper(str(temp_path))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/arxiv/{arxiv_id}")
async def get_arxiv_paper(arxiv_id: str):
    """Fetch and process a paper from arXiv."""
    try:
        result = await paper_processor.process_paper("", arxiv_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_question(question: str, paper_id: str):
    """Ask a question about a paper."""
    try:
        # Get similar Q&A pairs for context
        similar_qa = embedding_clustering.get_similar_qa_pairs(question)
        context = "\n\n".join([qa["text"] for qa in similar_qa])
        
        # Generate response using Ollama
        response = await ollama.generate_response(question, context)
        formatted_response = ollama.format_response(response)
        
        if formatted_response["success"]:
            # Store the Q&A pair
            embedding_clustering.store_qa_pair(
                question,
                formatted_response["answer"],
                paper_id
            )
        
        return formatted_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters")
async def get_clusters():
    """Get the current cluster hierarchy for visualization."""
    try:
        # Get all Q&A pairs from ChromaDB
        results = embedding_clustering.collection.get()
        
        if not results["documents"]:
            return {"name": "root", "children": []}
        
        # Generate embeddings for all questions
        questions = [doc.split("\n")[0][3:] for doc in results["documents"]]
        embeddings = embedding_clustering.get_embeddings(questions)
        
        # Cluster the embeddings
        umap_embeddings, clusterer = embedding_clustering.cluster_embeddings(embeddings)
        
        # Generate hierarchy for visualization
        hierarchy = embedding_clustering.get_cluster_hierarchy(umap_embeddings, clusterer)
        
        return hierarchy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 