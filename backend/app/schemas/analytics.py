"""Analytics and telemetry schemas."""
from typing import List, Dict, Any
from pydantic import BaseModel


class SystemMetricsOut(BaseModel):
    total_documents: int
    processed_documents: int
    failed_documents: int
    total_conversations: int
    total_ai_queries: int
    total_reports: int
    agent_tasks_completed: int
    avg_response_time_ms: float
    total_tokens_consumed: int
    estimated_api_cost: float
    processing_queue_status: str
    recent_activities: List[Dict[str, Any]]
    documents_by_type: Dict[str, int]
    query_trends: List[Dict[str, Any]]
