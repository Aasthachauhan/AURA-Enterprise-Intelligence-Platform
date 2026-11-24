"""Tests for MCP Tool discovery, input validation, and execution."""
import pytest
from app.mcp.client import mcp_client
from app.mcp.tools import execute_local_mcp_tool


@pytest.mark.asyncio
async def test_mcp_tool_discovery():
    """Verify MCP tools are discovered with schema definitions."""
    tools = mcp_client.list_tools()
    assert len(tools) >= 5
    tool_names = [t["name"] for t in tools]
    assert "search_documents" in tool_names
    assert "get_system_health" in tool_names
    assert "generate_report" in tool_names


@pytest.mark.asyncio
async def test_mcp_local_tool_execution():
    """Verify local MCP tool execution returns structured health diagnostics."""
    health_result = await execute_local_mcp_tool(
        tool_name="get_system_health",
        arguments={"check_type": "standard"},
        workspace_id="test_ws"
    )
    assert health_result["status"] == "healthy"
    assert "cpu_percent" in health_result
    assert health_result["mcp_server"] == "active"
