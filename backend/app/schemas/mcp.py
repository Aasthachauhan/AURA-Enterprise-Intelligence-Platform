"""MCP (Model Context Protocol) tool schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class MCPToolSchema(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    is_sensitive: bool = False
    requires_approval: bool = False


class MCPExecuteRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class MCPExecuteResponse(BaseModel):
    tool_name: str
    status: str
    result: Any
    is_error: bool = False
    duration_ms: int = 0
