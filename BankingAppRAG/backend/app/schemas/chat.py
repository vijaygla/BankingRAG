from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer question or instruction")
    session_id: Optional[str] = Field(None, description="Session ID for sliding-window memory context")
    model: Optional[str] = Field(None, description="Select AI model: openai.gpt-5, openai.gpt-4o, anthropic.claude-opus-4-6-v1, grok-4")

class CitationItem(BaseModel):
    filename: str
    title: str
    chunk_index: int
    score: float
    snippet: str

class ChatQueryResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    answer: str
    intent: str # POLICY_DOC, USER_SQL, REFUSE_OOS
    citations: List[CitationItem] = []
    model_used: str
    latency_ms: float
    tokens_used: int
    session_id: str
    cached: bool = False

class ChatFeedbackRequest(BaseModel):
    message_id: Optional[int] = None
    rating: int = Field(..., ge=-1, le=5, description="1 to 5 rating, or 1 (thumbs up) / -1 (thumbs down)")
    comment: Optional[str] = None

class ChatMessageHistoryItem(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}
    id: int
    role: str
    content: str
    intent: Optional[str] = None
    model_used: Optional[str] = None
    created_at: datetime
