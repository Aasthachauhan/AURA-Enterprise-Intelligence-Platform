"""Typed State representation for LangGraph multi-agent workflow."""
from typing import TypedDict, List, Dict, Any, Optional


class AURAState(TypedDict):
    task_id: str
    workspace_id: str
    user_id: Optional[str]
    query: str
    selected_document_ids: Optional[List[str]]
    
    # Supervisor planning
    plan_steps: List[Dict[str, Any]]
    current_step_name: Optional[str]
    next_agent: Optional[str]
    
    # Evidence & Agent Findings
    research_findings: List[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    extracted_entities: List[Dict[str, Any]]
    analytical_insights: List[Dict[str, Any]]
    
    # Execution & Tools
    tool_calls: List[Dict[str, Any]]
    requires_approval: bool
    approval_prompt: Optional[str]
    is_approved: Optional[bool]
    
    # Verification & Citations
    verification_passed: bool
    verification_feedback: Optional[str]
    citations: List[Dict[str, Any]]
    
    # Final Output
    final_response: Optional[str]
    report_id: Optional[str]
    
    # Execution metadata
    retry_count: int
    max_retries: int
    duration_ms: int
    status: str
    error: Optional[str]
