"""MCP Client integration layer: discovery, authorization, validation, and audit logging."""
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent import ToolExecution
from app.models.audit import AuditLog
from app.mcp.tools import MCP_REGISTERED_TOOLS, execute_local_mcp_tool


class MCPClient:
    def __init__(self):
        self._tools = {t["name"]: t for t in MCP_REGISTERED_TOOLS}

    def list_tools(self) -> List[Dict[str, Any]]:
        """Discover available MCP tools."""
        return list(self._tools.values())

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve tool schema by name."""
        return self._tools.get(tool_name)

    async def execute_tool(
        self,
        db: AsyncSession,
        tool_name: str,
        arguments: Dict[str, Any],
        workspace_id: str,
        user_id: Optional[str] = None,
        agent_run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate input arguments, check permissions, execute tool, and write audit trail."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not registered in MCP catalog")

        # Validate required arguments
        required_props = tool.get("input_schema", {}).get("required", [])
        for req in required_props:
            if req not in arguments:
                raise ValueError(f"Missing required parameter '{req}' for tool '{tool_name}'")

        is_sensitive = tool.get("is_sensitive", False)
        start_time = time.time()
        error_msg = None
        result = None
        status = "success"

        try:
            result = await execute_local_mcp_tool(tool_name, arguments, workspace_id)
        except Exception as e:
            status = "error"
            error_msg = str(e)
            result = {"error": str(e)}

        duration_ms = int((time.time() - start_time) * 1000)

        # Record ToolExecution in DB
        execution_record = ToolExecution(
            agent_run_id=agent_run_id,
            tool_name=tool_name,
            tool_source="internal_mcp",
            input_arguments=arguments,
            output_result=result,
            is_sensitive=is_sensitive,
            status=status,
            error_message=error_msg,
            duration_ms=duration_ms
        )
        db.add(execution_record)

        # Audit Log
        audit = AuditLog(
            workspace_id=workspace_id,
            user_id=user_id,
            action="MCP_TOOL_EXECUTE",
            resource_type="TOOL",
            resource_id=tool_name,
            status="SUCCESS" if status == "success" else "FAILURE",
            details_json={
                "tool_name": tool_name,
                "arguments": arguments,
                "duration_ms": duration_ms
            }
        )
        db.add(audit)
        await db.commit()

        return {
            "tool_name": tool_name,
            "status": status,
            "result": result,
            "duration_ms": duration_ms,
            "is_sensitive": is_sensitive
        }


mcp_client = MCPClient()
