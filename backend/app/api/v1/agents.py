"""AI Agents API router."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.models.agent import AgentRun, ToolExecution
from app.schemas.agent import AgentRunCreate, ApprovalDecision, AgentRunOut, ToolExecutionOut
from app.agents.graph import aura_agent_app

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.get("/runs", response_model=List[AgentRunOut])
async def list_agent_runs(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List recent agent executions and multi-agent workflow traces."""
    res = await db.execute(
        select(AgentRun).filter(AgentRun.workspace_id == workspace.id).order_by(AgentRun.created_at.desc()).limit(50)
    )
    runs = res.scalars().all()
    return [AgentRunOut.model_validate(r) for r in runs]


@router.get("/tools/executions", response_model=List[ToolExecutionOut])
async def list_tool_executions(
    db: AsyncSession = Depends(get_db)
):
    """List tool executions audit trail."""
    res = await db.execute(select(ToolExecution).order_by(ToolExecution.created_at.desc()).limit(50))
    executions = res.scalars().all()
    return [ToolExecutionOut.model_validate(e) for e in executions]


@router.post("/approval/{agent_run_id}")
async def approve_sensitive_action(
    agent_run_id: str,
    decision: ApprovalDecision,
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Submit human-in-the-loop approval or rejection for paused tool executions."""
    res = await db.execute(
        select(AgentRun).filter(AgentRun.id == agent_run_id, AgentRun.workspace_id == workspace.id)
    )
    run = res.scalars().first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")

    run.is_approved = decision.approved
    run.status = "completed" if decision.approved else "rejected"
    if not decision.approved:
        run.error_message = f"Execution rejected by user: {decision.reason or 'No reason provided'}"
        
    await db.commit()
    await db.refresh(run)
    return {"message": "Decision recorded", "is_approved": decision.approved, "status": run.status}


@router.post("/execute", response_model=AgentRunOut)
async def execute_agent_mission(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Dispatch an autonomous multi-agent mission from the AI Agents Workspace."""
    import time
    from app.agents.graph import aura_agent_app
    query = payload.get("query") or payload.get("task")
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query or mission goal is required")

    agent_type = payload.get("agent_type", "supervisor")
    start_time = time.time()

    initial_state = {
        "task_id": f"mission-{int(time.time())}",
        "workspace_id": workspace.id,
        "user_id": current_user.id,
        "query": query,
        "selected_document_ids": payload.get("document_ids"),
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
    duration_ms = int((time.time() - start_time) * 1000)

    agent_run = AgentRun(
        workspace_id=workspace.id,
        user_id=current_user.id,
        agent_type=agent_type,
        workflow_name=f"{agent_type.capitalize()} Mission",
        status="completed",
        input_payload={"query": query},
        output_payload={
            "response": output_state.get("final_response", "Mission completed successfully."),
            "citations": output_state.get("citations", [])
        },
        plan_steps=output_state.get("plan_steps", []),
        duration_ms=duration_ms
    )
    db.add(agent_run)
    await db.commit()
    await db.refresh(agent_run)
    return AgentRunOut.model_validate(agent_run)
