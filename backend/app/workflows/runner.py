"""Workflow runner executing multi-step business pipelines."""
import time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.workflows.definitions import PRECONFIGURED_WORKFLOWS
from app.services.report_service import ReportService
from app.models.agent import AgentRun


class WorkflowRunner:
    @staticmethod
    def list_templates() -> List[Dict[str, Any]]:
        """Return available workflow templates."""
        return PRECONFIGURED_WORKFLOWS

    @staticmethod
    async def execute_workflow(
        db: AsyncSession,
        workflow_id: str,
        document_ids: List[str],
        custom_instructions: str,
        workspace_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Execute autonomous workflow pipeline using multi-agent system."""
        wf_template = next((w for w in PRECONFIGURED_WORKFLOWS if w["id"] == workflow_id), None)
        if not wf_template:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        start_time = time.time()
        
        # Create AgentRun tracking record
        agent_run = AgentRun(
            workspace_id=workspace_id,
            user_id=user_id,
            agent_type="supervisor",
            workflow_name=wf_template["name"],
            status="running",
            input_payload={"workflow_id": workflow_id, "document_ids": document_ids},
            plan_steps=[{"step": s, "status": "pending"} for s in wf_template["steps"]],
            current_step=wf_template["steps"][0]
        )
        db.add(agent_run)
        await db.commit()
        await db.refresh(agent_run)

        # Generate report
        focus = custom_instructions or wf_template["description"]
        report = await ReportService.generate_report(
            db=db,
            title=f"{wf_template['name']} Report",
            report_type=workflow_id,
            document_ids=document_ids,
            query_or_focus=focus,
            workspace_id=workspace_id,
            user_id=user_id
        )

        duration_ms = int((time.time() - start_time) * 1000)

        # Update AgentRun to completed
        agent_run.status = "completed"
        agent_run.output_payload = {"report_id": report.id, "title": report.title}
        agent_run.duration_ms = duration_ms
        agent_run.plan_steps = [{"step": s, "status": "completed"} for s in wf_template["steps"]]
        await db.commit()

        return {
            "workflow_id": workflow_id,
            "workflow_name": wf_template["name"],
            "status": "completed",
            "report_id": report.id,
            "report_title": report.title,
            "duration_ms": duration_ms,
            "steps_executed": len(wf_template["steps"])
        }
