"""LangGraph Multi-Agent Orchestration State Machine."""
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.agents.state import AURAState
from app.agents.supervisor import SupervisorAgent
from app.agents.research import ResearchAgent
from app.agents.document_intelligence import DocumentIntelligenceAgent
from app.agents.analytical import AnalyticalAgent
from app.agents.execution import ExecutionAgent
from app.agents.report_generation import ReportGenerationAgent
from app.agents.verification import VerificationAgent


def build_aura_agent_graph() -> StateGraph:
    """Construct the LangGraph state machine with conditional routing and bounded cycles."""
    workflow = StateGraph(AURAState)

    # 1. Add Agent Nodes
    workflow.add_node("supervisor", SupervisorAgent.plan)
    workflow.add_node("research", ResearchAgent.run)
    workflow.add_node("document_intelligence", DocumentIntelligenceAgent.run)
    workflow.add_node("analytical", AnalyticalAgent.run)
    workflow.add_node("execution", ExecutionAgent.run)
    workflow.add_node("report_generation", ReportGenerationAgent.run)
    workflow.add_node("verification", VerificationAgent.run)

    # 2. Set Entry Point
    workflow.set_entry_point("supervisor")

    # 3. Define Conditional Routing from Supervisor
    def route_from_supervisor(state: AURAState) -> str:
        next_ag = state.get("next_agent", "research")
        return next_ag if next_ag in ["research", "document_intelligence", "analytical"] else "research"

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "research": "research",
            "document_intelligence": "document_intelligence",
            "analytical": "analytical"
        }
    )

    # 4. Research flows to Document Intelligence or Analytical
    def route_from_research(state: AURAState) -> str:
        plan = state.get("plan_steps", [])
        has_doc_intel = any(s.get("agent") == "document_intelligence" for s in plan)
        return "document_intelligence" if has_doc_intel else "analytical"

    workflow.add_conditional_edges(
        "research",
        route_from_research,
        {
            "document_intelligence": "document_intelligence",
            "analytical": "analytical"
        }
    )

    workflow.add_edge("document_intelligence", "analytical")

    # 5. Analytical flows to Tool Execution or Report Generation
    def route_from_analytical(state: AURAState) -> str:
        plan = state.get("plan_steps", [])
        has_exec = any(s.get("agent") == "execution" for s in plan)
        if has_exec:
            return "execution"
        return "report_generation"

    workflow.add_conditional_edges(
        "analytical",
        route_from_analytical,
        {
            "execution": "execution",
            "report_generation": "report_generation"
        }
    )

    # 6. Execution flows to Report Generation or approval pause
    def route_from_execution(state: AURAState) -> str:
        if state.get("requires_approval") and not state.get("is_approved"):
            return END
        return "report_generation"

    workflow.add_conditional_edges(
        "execution",
        route_from_execution,
        {
            END: END,
            "report_generation": "report_generation"
        }
    )

    workflow.add_edge("report_generation", "verification")

    # 7. Verification: bounded retry loop
    def route_from_verification(state: AURAState) -> str:
        if state.get("verification_passed"):
            return END
        retry = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 1)
        if retry < max_retries:
            return "research"
        return END

    workflow.add_conditional_edges(
        "verification",
        route_from_verification,
        {
            END: END,
            "research": "research"
        }
    )

    return workflow.compile()


# Compiled LangGraph Application instance
aura_agent_app = build_aura_agent_graph()
