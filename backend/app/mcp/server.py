"""Local MCP Server implementation conforming to Model Context Protocol."""
import json
from typing import Dict, Any, List
from app.mcp.tools import MCP_REGISTERED_TOOLS, execute_local_mcp_tool


class LocalMCPServer:
    """In-process and JSON-RPC Model Context Protocol Server."""
    def __init__(self, name: str = "AURA-Local-MCP-Server", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools = {t["name"]: t for t in MCP_REGISTERED_TOOLS}

    def handle_json_rpc(self, request_data: Dict[str, Any], workspace_id: str = "default") -> Dict[str, Any]:
        """Handle JSON-RPC MCP request."""
        req_id = request_data.get("id", 1)
        method = request_data.get("method")
        params = request_data.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": list(self.tools.values())}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method/Tool '{tool_name}' not found"}
                }
            try:
                import asyncio
                res = asyncio.run(execute_local_mcp_tool(tool_name, args, workspace_id))
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res)}]}
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }


local_mcp_server = LocalMCPServer()
