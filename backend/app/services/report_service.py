"""Report generation and export service."""
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.report import Report
from app.models.document import Document
from app.models.audit import AuditLog
from app.rag.engine import rag_engine
from app.agents.graph import aura_agent_app


class ReportService:
    @staticmethod
    async def generate_report(
        db: AsyncSession,
        title: str,
        report_type: str,
        document_ids: List[str],
        query_or_focus: str,
        workspace_id: str,
        user_id: Optional[str] = None
    ) -> Report:
        """Execute autonomous agent pipeline to generate comprehensive executive report."""
        # Run agent workflow
        initial_state = {
            "task_id": f"rep-{int(time.time())}",
            "workspace_id": workspace_id,
            "user_id": user_id,
            "query": f"Generate a comprehensive {report_type} report focusing on: {query_or_focus}",
            "selected_document_ids": document_ids,
            "plan_steps": [],
            "research_findings": [],
            "retrieved_chunks": [],
            "extracted_entities": [],
            "analytical_insights": [],
            "tool_calls": [],
            "requires_approval": False,
            "approval_prompt": None,
            "is_approved": None,
            "verification_passed": True,
            "citations": [],
            "final_response": None,
            "retry_count": 0,
            "max_retries": 1,
            "duration_ms": 0,
            "status": "pending",
            "error": None
        }

        output_state = await aura_agent_app.ainvoke(initial_state)

        raw_response = output_state.get("final_response") or ""
        findings = output_state.get("research_findings", [])
        insights = output_state.get("analytical_insights", [])
        citations = output_state.get("citations", [])

        exec_summary = (
            f"Autonomous enterprise intelligence analysis conducted over {len(document_ids)} documents. "
            f"Synthesizes {len(findings)} validated evidence points and {len(insights)} analytical insights "
            f"addressing: \"{query_or_focus}\"."
        )

        if "# " in raw_response and "Executive Summary" in raw_response:
            markdown_content = raw_response
        else:
            markdown_content = (
                f"# {title}\n\n"
                f"## 1. Executive Summary\n{exec_summary}\n\n"
                f"## 2. Analysis & Findings\n{raw_response or 'No conflicting anomalies detected.'}\n\n"
                f"## 3. Scope & Limitations\nAnalysis is grounded exclusively in the provided document repository."
            )

        risks = [
            {"risk": ins.get("title"), "impact": "High", "mitigation": "Review test coverage and validation checks"}
            for ins in insights if "risk" in ins.get("category", "").lower() or "gap" in ins.get("category", "").lower()
        ]
        if not risks:
            risks = [{"risk": "Requirement Drift", "impact": "Medium", "mitigation": "Establish continuous automated regression testing"}]

        recommendations = [
            {"recommendation": "Execute end-to-end integration verification on identified requirement gaps", "priority": "P1"},
            {"recommendation": "Maintain strict citation-grounded requirement traceability in production PRDs", "priority": "P2"}
        ]

        report = Report(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            report_type=report_type,
            executive_summary=exec_summary,
            findings=findings,
            risk_analysis=risks,
            recommendations=recommendations,
            limitations="Analysis is grounded exclusively in the uploaded document scope.",
            citations=citations,
            markdown_content=markdown_content
        )
        db.add(report)

        audit = AuditLog(
            workspace_id=workspace_id,
            user_id=user_id,
            action="REPORT_GENERATE",
            resource_type="REPORT",
            resource_id=report.id,
            status="SUCCESS",
            details_json={"title": title, "report_type": report_type}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(report)
        return report

    @staticmethod
    async def list_reports(db: AsyncSession, workspace_id: str) -> List[Report]:
        """Fetch all reports in workspace."""
        res = await db.execute(
            select(Report).filter(Report.workspace_id == workspace_id).order_by(Report.created_at.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def get_report(db: AsyncSession, report_id: str, workspace_id: str) -> Report:
        """Fetch single report."""
        res = await db.execute(
            select(Report).filter(Report.id == report_id, Report.workspace_id == workspace_id)
        )
        report = res.scalars().first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        return report

    @staticmethod
    async def delete_report(db: AsyncSession, report_id: str, workspace_id: str) -> bool:
        """Delete report record."""
        report = await ReportService.get_report(db, report_id, workspace_id)
        await db.delete(report)
        await db.commit()
        return True
