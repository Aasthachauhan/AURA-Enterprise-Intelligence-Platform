"""Agent Run and Tool Execution models."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Float, Boolean
from app.core.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    agent_type = Column(String(100), nullable=False)  # "supervisor", "research", "document_intelligence", etc.
    workflow_name = Column(String(255), nullable=True)
    status = Column(String(50), default="running")  # "running", "completed", "failed", "waiting_approval"
    input_payload = Column(JSON, default=dict)
    output_payload = Column(JSON, default=dict)
    
    plan_steps = Column(JSON, default=list)
    current_step = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    total_tokens = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    duration_ms = Column(Integer, default=0)
    
    requires_approval = Column(Boolean, default=False)
    is_approved = Column(Boolean, nullable=True)
    approval_prompt = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime, nullable=True)


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    
    tool_name = Column(String(100), nullable=False, index=True)
    tool_source = Column(String(50), default="internal_mcp")  # "internal_mcp", "external_api", "system"
    input_arguments = Column(JSON, default=dict)
    output_result = Column(JSON, default=dict)
    
    is_sensitive = Column(Boolean, default=False)
    status = Column(String(50), default="success")  # "success", "error", "rejected"
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
