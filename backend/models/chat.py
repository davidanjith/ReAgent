from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Message(BaseModel):
    id: str
    chat_id: str
    content: str
    paper_id: Optional[str] = None
    created_at: datetime

class ChatBase(BaseModel):
    title: str
    paper_ids: List[str] = []

class ChatCreate(ChatBase):
    pass

class ChatUpdate(BaseModel):
    title: Optional[str] = None
    paper_ids: Optional[List[str]] = None

class Chat(ChatBase):
    id: str
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClusterBase(BaseModel):
    name: str
    description: Optional[str] = None
    paper_id: str

class ClusterCreate(ClusterBase):
    pass

class ClusterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Cluster(ClusterBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 