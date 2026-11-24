"""Unit tests for Knowledge Graph extraction, querying, and entity explorer."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_knowledge_graph_endpoints(client: AsyncClient, auth_headers: dict):
    """Test graph fetching and entity extraction from uploaded documents."""
    # 1. Upload a document with entities
    doc_content = b"""# Cloud Architecture Specification
The AURA system uses PostgreSQL with pgvector for dense vector storage.
The supervisor agent delegates subtasks to the research agent.
SLA requires sub-100ms API response latency and 99.95% availability.
Security is certified under SOC 2 Type II compliance standards."""

    upload_res = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": auth_headers["Authorization"], "X-Workspace-Id": auth_headers["X-Workspace-Id"]},
        files={"file": ("kg_test_spec.md", doc_content, "text/markdown")}
    )
    assert upload_res.status_code in [200, 201]
    doc_id = upload_res.json()["id"]

    # 2. Trigger entity and relation extraction
    extract_res = await client.post(
        f"/api/v1/knowledge-base/extract/{doc_id}",
        headers=auth_headers
    )
    assert extract_res.status_code == 200
    extract_data = extract_res.json()
    assert "entities_extracted" in extract_data
    assert extract_data["entities_extracted"] > 0

    # 3. Query knowledge graph for visualization
    graph_res = await client.get("/api/v1/knowledge-base/graph?limit=50", headers=auth_headers)
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert len(graph_data["nodes"]) > 0

    # Validate node schema for HTML5 Canvas rendering
    first_node = graph_data["nodes"][0]
    assert "id" in first_node
    assert "name" in first_node
    assert "type" in first_node
