import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.chat import Chat, ChatCreate, ChatUpdate, Message, Cluster, ClusterCreate, ClusterUpdate
from utils.ollama_interface import get_ollama_client
from utils.memory_service import memory_service
from utils.embedding_service import embedding_service

class ChatService:
    def __init__(self):
        self.chats = {}  # In-memory storage for chats
        self.client = get_ollama_client()

    def create_chat(self, chat: ChatCreate) -> Chat:
        chat_id = str(uuid.uuid4())
        new_chat = Chat(
            id=chat_id,
            **chat.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.chats[chat_id] = new_chat
        return new_chat

    def get_chat(self, chat_id: str) -> Optional[Chat]:
        return self.chats.get(chat_id)

    def get_all_chats(self) -> List[Chat]:
        return list(self.chats.values())

    def update_chat(self, chat_id: str, chat_update: ChatUpdate) -> Optional[Chat]:
        if chat_id not in self.chats:
            return None
        
        chat = self.chats[chat_id]
        update_data = chat_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(chat, field, value)
        
        chat.updated_at = datetime.utcnow()
        return chat

    def delete_chat(self, chat_id: str) -> bool:
        if chat_id in self.chats:
            del self.chats[chat_id]
            return True
        return False

    def add_message(self, chat_id: str, content: str, paper_id: Optional[str] = None) -> Optional[Message]:
        if chat_id not in self.chats:
            return None
        
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            chat_id=chat_id,
            content=content,
            paper_id=paper_id,
            created_at=datetime.utcnow()
        )
        
        chat = self.chats[chat_id]
        chat.messages.append(message)
        chat.updated_at = datetime.utcnow()
        
        return message

    async def process_question(self, paper_id: str, question: str) -> Dict[str, Any]:
        """Process a question about a paper and return an answer with context."""
        # Get relevant chunks from memory
        chunks = await memory_service.get_relevant_chunks(paper_id, question)
        
        # Prepare context from chunks
        context = "\n".join(chunk['text'] for chunk in chunks)
        
        # Generate answer using Ollama
        response = await self.client.chat(
            model="llama2",
            messages=[
                {"role": "system", "content": f"Answer the question based on the following context:\n\n{context}"},
                {"role": "user", "content": question}
            ]
        )
        
        # Store Q&A pair in memory
        qa_id = str(uuid.uuid4())
        await memory_service.store_qa_pair(paper_id, qa_id, question, response.message.content, chunks)
        
        return {
            "question": question,
            "answer": response.message.content,
            "context": chunks
        }

    async def get_chat_history(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a paper."""
        return await memory_service.get_paper_qa_pairs(paper_id)

    async def get_clusters(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get clusters for a paper's Q&A pairs."""
        return await memory_service.get_paper_clusters(paper_id)

class ClusterService:
    def __init__(self):
        self.clusters = {}  # In-memory storage for clusters

    def create_cluster(self, cluster: ClusterCreate) -> Cluster:
        cluster_id = str(uuid.uuid4())
        new_cluster = Cluster(
            id=cluster_id,
            **cluster.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.clusters[cluster_id] = new_cluster
        return new_cluster

    def get_cluster(self, cluster_id: str) -> Optional[Cluster]:
        return self.clusters.get(cluster_id)

    def get_all_clusters(self) -> List[Cluster]:
        return list(self.clusters.values())

    def update_cluster(self, cluster_id: str, cluster_update: ClusterUpdate) -> Optional[Cluster]:
        if cluster_id not in self.clusters:
            return None
        
        cluster = self.clusters[cluster_id]
        update_data = cluster_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(cluster, field, value)
        
        cluster.updated_at = datetime.utcnow()
        return cluster

    def delete_cluster(self, cluster_id: str) -> bool:
        if cluster_id in self.clusters:
            del self.clusters[cluster_id]
            return True
        return False

# Create service instances
chat_service = ChatService()
cluster_service = ClusterService() 