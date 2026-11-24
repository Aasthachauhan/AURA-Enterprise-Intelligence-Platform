"""MCP Integration API router."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.mcp import MCPToolSchema, MCPExecuteRequest, MCPExecuteResponse
from app.mcp.client import mcp_client
from app.mcp.server import local_mcp_server

router = APIRouter(prefix="/mcp", tags=["MCP Tools"])


@router.get("/tools", response_model=List[MCPToolSchema])
async def list_mcp_tools(
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace)
):
    """List all available MCP tools and their parameter schemas."""
    return mcp_client.list_tools()


@router.post("/execute", response_model=MCPExecuteResponse)
async def execute_tool(
    data: MCPExecuteRequest,
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Execute an MCP tool on behalf of the user or agent."""
    try:
        res = await mcp_client.execute_tool(
            db=db,
            tool_name=data.tool_name,
            arguments=data.arguments,
            workspace_id=workspace.id,
            user_id=current_user.id
        )
        return MCPExecuteResponse(
            tool_name=data.tool_name,
            status=res["status"],
            result=res["result"],
            is_error=res["status"] == "error",
            duration_ms=res["duration_ms"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rpc")
async def json_rpc_endpoint(
    payload: Dict[str, Any],
    workspace: Workspace = Depends(get_current_workspace)
):
    """JSON-RPC protocol endpoint for external MCP clients."""
    return local_mcp_server.handle_json_rpc(payload, workspace.id)
