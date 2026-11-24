"""Workflow template and execution schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class WorkflowTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str
    required_inputs: List[Dict[str, Any]]
    steps: List[str]
    estimated_duration: str


class WorkflowTriggerRequest(BaseModel):
    workflow_id: str
    document_ids: List[str]
    custom_instructions: Optional[str] = None
    parameters: Dict[str, Any] = {}
