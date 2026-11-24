"""Research Agent: Internal document retrieval and evidence collection."""
from typing import Dict, Any
from sqlalchemy.future import select
from app.agents.state import AURAState
from app.rag.engine import rag_engine
from app.core.database import AsyncSessionLocal


class ResearchAgent:
    @staticmethod
    async def run(state: AURAState) -> Dict[str, Any]:
        """Search internal documents and assemble structured evidence with citations."""
        query = state.get("query", "")
        workspace_id = state.get("workspace_id", "")
        doc_ids = state.get("selected_document_ids")

        async with AsyncSessionLocal() as db:
            rag_res = await rag_engine.answer_query(
                db=db,
                query=query,
                workspace_id=workspace_id,
                filter_document_ids=doc_ids,
                top_k=6
            )

        findings = []
        for c in rag_res.get("retrieved_chunks", []):
            findings.append({
                "source": c.get("document_title"),
                "page": c.get("page"),
                "sheet": c.get("sheet"),
                "section": c.get("section"),
                "evidence": c.get("content"),
                "relevance_score": c.get("score")
            })

        # Mark research step completed in plan
        plan_steps = state.get("plan_steps", [])
        for step in plan_steps:
            if step.get("agent") == "research":
                step["status"] = "completed"

        return {
            "research_findings": findings,
            "retrieved_chunks": rag_res.get("retrieved_chunks", []),
            "citations": rag_res.get("citations", []),
            "plan_steps": plan_steps,
            "current_step_name": "Evidence Gathering Completed"
        }
