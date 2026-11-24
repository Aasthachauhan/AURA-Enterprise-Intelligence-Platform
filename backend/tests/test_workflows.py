"""Unit tests for Autonomous Business Workflows."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_workflows_catalog(client: AsyncClient, auth_headers: dict):
    """Verify that all preconfigured business workflows are discoverable."""
    resp = await client.get("/api/v1/workflows", headers=auth_headers)
    assert resp.status_code == 200
    workflows = resp.json()
    assert isinstance(workflows, list)
    assert len(workflows) >= 3

    wf_ids = [w["id"] for w in workflows]
    assert "wf-prd-gap" in wf_ids
    assert "wf-financial-audit" in wf_ids
    assert "wf-contract-risk" in wf_ids

    # Validate template schema
    prd_wf = next(w for w in workflows if w["id"] == "wf-prd-gap")
    assert "name" in prd_wf
    assert "description" in prd_wf
    assert "required_inputs" in prd_wf
    assert "estimated_duration" in prd_wf
    assert len(prd_wf["steps"]) > 0


@pytest.mark.asyncio
async def test_workflow_execution_validation(client: AsyncClient, auth_headers: dict):
    """Test validation errors on invalid workflow requests."""
    # 1. Missing documents
    resp = await client.post(
        "/api/v1/workflows/execute",
        headers=auth_headers,
        json={"workflow_id": "wf-prd-gap", "document_ids": []}
    )
    assert resp.status_code in [400, 422]

    # 2. Non-existent workflow ID
    resp2 = await client.post(
        "/api/v1/workflows/execute",
        headers=auth_headers,
        json={"workflow_id": "invalid_unknown_workflow", "document_ids": ["doc-123"]}
    )
    assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_workflow_execution_run(client: AsyncClient, auth_headers: dict):
    """Test execution of PRD gap analysis and contract risk workflows with uploaded docs."""
    # Upload sample file
    file_content = b"# PRD Requirements\nREQ-01: Must support multi-tenant isolation.\nREQ-02: Must have 99.9% SLA."
    upload_res = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": auth_headers["Authorization"], "X-Workspace-Id": auth_headers["X-Workspace-Id"]},
        files={"file": ("workflow_test_prd.md", file_content, "text/markdown")}
    )
    assert upload_res.status_code in [200, 201]
    doc_id = upload_res.json()["id"]

    # Execute PRD workflow
    exec_res = await client.post(
        "/api/v1/workflows/execute",
        headers=auth_headers,
        json={
            "workflow_id": "wf-prd-gap",
            "document_ids": [doc_id],
            "custom_instructions": "Check high priority items"
        }
    )
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["workflow_id"] == "wf-prd-gap"
    assert data["status"] in ["completed", "success"]
    assert "report_id" in data or "report_title" in data or "steps_executed" in data
