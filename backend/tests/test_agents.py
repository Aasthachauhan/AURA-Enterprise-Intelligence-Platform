"""Tests for Multi-Agent Orchestration via LangGraph."""
import pytest
from app.agents.graph import aura_agent_app


@pytest.mark.asyncio
async def test_multi_agent_execution_cycle():
    """Verify LangGraph executes Supervisor -> Research -> Analytical -> Verification workflow."""
    initial_state = {
        "task_id": "test-agent-run-001",
        "workspace_id": "ws-test",
        "user_id": "u-test",
        "query": "Analyze product requirements and identify release risks",
        "selected_document_ids": None,
        "plan_steps": [],
        "research_findings": [
            {"source": "sample_prd.md", "page": 1, "evidence": "Latency limit shall not exceed 300ms."}
        ],
        "retrieved_chunks": [],
        "extracted_entities": [],
        "analytical_insights": [],
        "tool_calls": [],
        "requires_approval": False,
        "approval_prompt": None,
        "is_approved": None,
        "verification_passed": True,
        "citations": [{"document_title": "sample_prd.md", "page_number": 1, "excerpt": "Latency limit shall not exceed 300ms"}],
        "final_response": None,
        "retry_count": 0,
        "max_retries": 1,
        "duration_ms": 0,
        "status": "pending",
        "error": None
    }

    result = await aura_agent_app.ainvoke(initial_state)

    assert result is not None
    assert result.get("verification_passed") is True
    assert result.get("final_response") is not None
    assert len(result.get("plan_steps", [])) > 0
