"""Chat and message schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class CitationItem(BaseModel):
    document_id: str
    document_title: str
    page_number: Optional[int] = None
    sheet_name: Optional[str] = None
    section_title: Optional[str] = None
    excerpt: str
    similarity_score: Optional[float] = None


class MessageCreate(BaseModel):
    content: str
    selected_document_ids: Optional[List[str]] = None
    use_agents: bool = True
    stream: bool = False


class MessageFeedback(BaseModel):
    rating: int  # 1 or -1
    notes: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    citations_json: List[Dict[str, Any]] = []
    agent_steps_json: List[Dict[str, Any]] = []
    tool_calls_json: List[Dict[str, Any]] = []
    tokens_prompt: int = 0
    tokens_completion: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    feedback_rating: Optional[int] = None
    feedback_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_pinned: Optional[bool] = None


class ConversationOut(BaseModel):
    id: str
    workspace_id: str
    title: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True
