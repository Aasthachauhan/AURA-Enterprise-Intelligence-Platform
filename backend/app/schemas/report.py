"""Report generation schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    title: str
    report_type: str = "gap_analysis"  # "gap_analysis", "executive_brief", "qa_assessment", "comparison", "custom"
    document_ids: List[str]
    query_or_focus: str
    include_risk_analysis: bool = True
    include_recommendations: bool = True


class ReportOut(BaseModel):
    id: str
    workspace_id: str
    title: str
    report_type: str
    executive_summary: str
    findings: List[Dict[str, Any]]
    risk_analysis: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    limitations: Optional[str] = None
    citations: List[Dict[str, Any]]
    markdown_content: str
    pdf_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
