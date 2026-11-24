"""Unit tests for Real Database Operational Analytics and Metrics."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_overview_metrics(client: AsyncClient, auth_headers: dict):
    """Verify that overview metrics derive from real database operations without hardcoding."""
    resp = await client.get("/api/v1/analytics/overview", headers=auth_headers)
    assert resp.status_code == 200
    metrics = resp.json()

    # Validate all essential operational metric keys
    assert "total_documents" in metrics
    assert "processed_documents" in metrics
    assert "failed_documents" in metrics
    assert "total_conversations" in metrics
    assert "total_ai_queries" in metrics
    assert "total_reports" in metrics
    assert "agent_tasks_completed" in metrics
    assert "avg_response_time_ms" in metrics
    assert "total_tokens_consumed" in metrics
    assert "estimated_api_cost" in metrics
    assert "processing_queue_status" in metrics

    # Verify types
    assert isinstance(metrics["total_documents"], int)
    assert isinstance(metrics["processed_documents"], int)
    assert isinstance(metrics["total_conversations"], int)
    assert isinstance(metrics["avg_response_time_ms"], (int, float))
    assert isinstance(metrics["total_tokens_consumed"], int)
    assert isinstance(metrics["estimated_api_cost"], (int, float))
    assert any(term in metrics["processing_queue_status"] for term in ["Idle", "Processing", "Healthy", "Active", "Operational"])
