"""Report and export models."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    report_type = Column(String(100), default="general")  # "gap_analysis", "executive_brief", "qa_assessment", "custom"
    
    executive_summary = Column(Text, nullable=False)
    findings = Column(JSON, default=list)  # list of findings with evidence
    risk_analysis = Column(JSON, default=list)  # list of risks
    recommendations = Column(JSON, default=list)  # list of recommendations
    limitations = Column(Text, nullable=True)
    citations = Column(JSON, default=list)  # list of references
    
    markdown_content = Column(Text, nullable=False)
    pdf_path = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", back_populates="reports")
    creator = relationship("User", back_populates="reports")
