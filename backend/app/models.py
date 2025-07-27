from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []
    session_id: str