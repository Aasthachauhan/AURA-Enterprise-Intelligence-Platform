"""Supervisor / Orchestrator Agent: Subtask decomposition, planning, and routing."""
from typing import Dict, Any, List
from app.agents.state import AURAState


class SupervisorAgent:
    @staticmethod
    def plan(state: AURAState) -> Dict[str, Any]:
        """
        Analyze request, classify intent, break into discrete subtasks,
        and assign required agents.
        """
        query = state.get("query", "").lower()
        
        # Check task characteristics
        is_report_request = any(kw in query for kw in ["report", "assessment", "summary", "generate"])
        is_comparison_request = any(kw in query for kw in ["compare", "difference", "conflict", "missing", "gap"])
        is_tool_request = any(kw in query for kw in ["execute", "tool", "query data", "health", "system"])
        
        steps: List[Dict[str, Any]] = [
            {"step_id": 1, "agent": "supervisor", "name": "Task Planning & Decomposition", "status": "completed"}
        ]
        
        # Dynamically compose workflow stages
        if is_comparison_request or "prd" in query or "requirement" in query:
            steps.append({"step_id": 2, "agent": "research", "name": "Document Retrieval & Evidence Gathering", "status": "pending"})
            steps.append({"step_id": 3, "agent": "document_intelligence", "name": "Entity & Requirement Extraction", "status": "pending"})
            steps.append({"step_id": 4, "agent": "analytical", "name": "Gap & Risk Analysis", "status": "pending"})
            if is_tool_request:
                steps.append({"step_id": 5, "agent": "execution", "name": "Authorized Tool Execution", "status": "pending"})
            steps.append({"step_id": 6, "agent": "report_generation", "name": "Report Synthesis", "status": "pending"})
            steps.append({"step_id": 7, "agent": "verification", "name": "Fact Checking & Citation Validation", "status": "pending"})
        elif is_report_request:
            steps.append({"step_id": 2, "agent": "research", "name": "Context Retrieval", "status": "pending"})
            steps.append({"step_id": 3, "agent": "analytical", "name": "Information Synthesis", "status": "pending"})
            steps.append({"step_id": 4, "agent": "report_generation", "name": "Executive Report Generation", "status": "pending"})
            steps.append({"step_id": 5, "agent": "verification", "name": "Citation & Claim Verification", "status": "pending"})
        else:
            steps.append({"step_id": 2, "agent": "research", "name": "Evidence Retrieval", "status": "pending"})
            steps.append({"step_id": 3, "agent": "analytical", "name": "Reasoning & Grounding", "status": "pending"})
            steps.append({"step_id": 4, "agent": "verification", "name": "Verification", "status": "pending"})

        return {
            "plan_steps": steps,
            "current_step_name": steps[1]["name"],
            "next_agent": steps[1]["agent"],
            "status": "in_progress"
        }
