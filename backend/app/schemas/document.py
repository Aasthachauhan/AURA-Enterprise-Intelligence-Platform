"""Document schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    workspace_id: str
    title: str
    filename: str
    file_type: str
    file_size_bytes: int
    category: str
    status: str
    error_message: Optional[str] = None
    version: int
    page_count: int
    chunk_count: int
    metadata_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentChunkOut(BaseModel):
    id: str
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    sheet_name: Optional[str] = None
    section_title: Optional[str] = None
    metadata_json: Dict[str, Any]

    class Config:
        from_attributes = True
