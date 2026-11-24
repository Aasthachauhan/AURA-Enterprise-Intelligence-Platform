"""Execution Agent: MCP and external tool execution with human-in-the-loop approvals."""
from typing import Dict, Any
from app.agents.state import AURAState
from app.mcp.tools import execute_local_mcp_tool


class ExecutionAgent:
    @staticmethod
    async def run(state: AURAState) -> Dict[str, Any]:
        """Execute authorized tools or checkpoint for human approval if action is sensitive."""
        query = state.get("query", "").lower()
        tool_calls = state.get("tool_calls", [])
        requires_approval = False
        approval_prompt = None

        if "delete" in query or "modify" in query or "purge" in query:
            # Sensitive operation requires approval
            requires_approval = True
            approval_prompt = f"Approval required to execute requested modification: '{state.get('query')}'"
            return {
                "requires_approval": True,
                "approval_prompt": approval_prompt,
                "status": "waiting_approval",
                "current_step_name": "Awaiting Human-in-the-Loop Approval"
            }

        # Safe read/analysis operations
        tool_name = "search_documents"
        res = await execute_local_mcp_tool(
            tool_name="get_system_health",
            arguments={"check_type": "deep"},
            workspace_id=state.get("workspace_id", "")
        )
        
        tool_calls.append({
            "tool_name": "get_system_health",
            "arguments": {"check_type": "deep"},
            "result": res,
            "status": "success"
        })

        plan_steps = state.get("plan_steps", [])
        for step in plan_steps:
            if step.get("agent") == "execution":
                step["status"] = "completed"

        return {
            "tool_calls": tool_calls,
            "requires_approval": False,
            "plan_steps": plan_steps,
            "current_step_name": "Tool Execution Completed"
        }
