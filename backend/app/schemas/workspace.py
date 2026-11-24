"""Workspace schemas."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceOut(BaseModel):
    id: str
    organization_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    is_default: bool
    created_at: datetime
    document_count: Optional[int] = 0

    class Config:
        from_attributes = True
