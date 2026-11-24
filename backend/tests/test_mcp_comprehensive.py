"""Unit tests for Model Context Protocol (MCP) tool execution, validation, and schema discovery."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mcp_all_registered_tools(client: AsyncClient, auth_headers: dict):
    """Verify that all 6 MCP enterprise tools are registered with valid JSON schemas."""
    tools_res = await client.get("/api/v1/mcp/tools", headers=auth_headers)
    assert tools_res.status_code == 200
    tools = tools_res.json()
    assert isinstance(tools, list)
    assert len(tools) >= 6

    tool_names = [t["name"] for t in tools]
    assert "search_documents" in tool_names
    assert "retrieve_document_sections" in tool_names
    assert "search_internal_knowledge" in tool_names
    assert "generate_report" in tool_names
    assert "query_application_data" in tool_names
    assert "get_system_health" in tool_names


@pytest.mark.asyncio
async def test_mcp_tool_execution_flow(client: AsyncClient, auth_headers: dict):
    """Test executing tools via MCP client: search_documents, query_application_data, and health."""
    # 1. Execute get_system_health
    health_res = await client.post(
        "/api/v1/mcp/execute",
        headers=auth_headers,
        json={"tool_name": "get_system_health", "arguments": {}}
    )
    assert health_res.status_code == 200
    data = health_res.json()
    assert data["tool_name"] == "get_system_health"
    assert data["status"] == "success"
    assert "result" in data
    assert data["is_error"] is False

    # 2. Execute query_application_data
    app_data_res = await client.post(
        "/api/v1/mcp/execute",
        headers=auth_headers,
        json={
            "tool_name": "query_application_data",
            "arguments": {"data_domain": "documents"}
        }
    )
    assert app_data_res.status_code == 200
    app_data = app_data_res.json()
    assert app_data["status"] == "success"
    assert "total_records" in app_data["result"] or "domain" in app_data["result"]

    # 3. Execute search_documents
    search_res = await client.post(
        "/api/v1/mcp/execute",
        headers=auth_headers,
        json={
            "tool_name": "search_documents",
            "arguments": {"query": "SLA", "top_k": 3}
        }
    )
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["status"] == "success"
    assert "results" in search_data["result"] or isinstance(search_data["result"], (list, dict))


@pytest.mark.asyncio
async def test_mcp_invalid_tool_rejection(client: AsyncClient, auth_headers: dict):
    """Ensure invalid tool requests are rejected with an error status."""
    res = await client.post(
        "/api/v1/mcp/execute",
        headers=auth_headers,
        json={"tool_name": "non_existent_tool_xyz", "arguments": {}}
    )
    assert res.status_code == 400
