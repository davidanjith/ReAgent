from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class PaperBase(BaseModel):
    title: str
    authors: List[str]
    content: str
    metadata: Optional[Dict[str, Any]] = None

class PaperCreate(PaperBase):
    pass

class PaperUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Paper(PaperBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 