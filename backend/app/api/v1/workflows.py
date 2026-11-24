"""Workflows API router."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workflow import WorkflowTemplate, WorkflowTriggerRequest
from app.workflows.runner import WorkflowRunner

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=List[WorkflowTemplate])
async def list_workflows():
    """List preconfigured autonomous enterprise workflow templates."""
    return WorkflowRunner.list_templates()


@router.post("/execute", response_model=Dict[str, Any])
async def execute_workflow(
    data: WorkflowTriggerRequest,
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Trigger an autonomous multi-step workflow execution."""
    if not data.document_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="document_ids list cannot be empty")
    try:
        return await WorkflowRunner.execute_workflow(
            db=db,
            workflow_id=data.workflow_id,
            document_ids=data.document_ids,
            custom_instructions=data.custom_instructions or "",
            workspace_id=workspace.id,
            user_id=current_user.id
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
