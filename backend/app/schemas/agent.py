"""Agent and tool execution schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class AgentRunCreate(BaseModel):
    agent_type: str  # "supervisor", "research", "document_intelligence", "analytical", "execution", "report_generation", "verification"
    workflow_name: Optional[str] = None
    task_description: str
    selected_document_ids: Optional[List[str]] = None
    parameters: Dict[str, Any] = {}


class ApprovalDecision(BaseModel):
    approved: bool
    reason: Optional[str] = None


class AgentRunOut(BaseModel):
    id: str
    workspace_id: str
    conversation_id: Optional[str] = None
    agent_type: str
    workflow_name: Optional[str] = None
    status: str
    input_payload: Dict[str, Any]
    output_payload: Dict[str, Any]
    plan_steps: List[Dict[str, Any]]
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    total_tokens: int = 0
    cost_estimate: float = 0.0
    duration_ms: int = 0
    requires_approval: bool = False
    is_approved: Optional[bool] = None
    approval_prompt: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ToolExecutionOut(BaseModel):
    id: str
    agent_run_id: Optional[str] = None
    tool_name: str
    tool_source: str
    input_arguments: Dict[str, Any]
    output_result: Dict[str, Any]
    is_sensitive: bool
    status: str
    error_message: Optional[str] = None
    duration_ms: int
    created_at: datetime

    class Config:
        from_attributes = True
