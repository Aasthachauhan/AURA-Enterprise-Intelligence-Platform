"""Audit log model for security compliance."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=True, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)  # "LOGIN", "DOCUMENT_UPLOAD", "AGENT_RUN", "TOOL_EXECUTE", "REPORT_GENERATE"
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    
    ip_address = Column(String(50), nullable=True)
    status = Column(String(50), default="SUCCESS")  # "SUCCESS", "FAILURE", "BLOCKED"
    details_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
