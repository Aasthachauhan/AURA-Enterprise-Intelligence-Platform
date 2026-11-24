"""Reports API router."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.report import ReportGenerateRequest, ReportOut
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=ReportOut)
async def generate_report(
    data: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Generate an evidence-backed intelligence report."""
    return await ReportService.generate_report(
        db=db,
        title=data.title,
        report_type=data.report_type,
        document_ids=data.document_ids,
        query_or_focus=data.query_or_focus,
        workspace_id=workspace.id,
        user_id=current_user.id
    )


@router.get("", response_model=List[ReportOut])
async def list_reports(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List all reports in the workspace."""
    reports = await ReportService.list_reports(db=db, workspace_id=workspace.id)
    return [ReportOut.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Get single report by ID."""
    report = await ReportService.get_report(db=db, report_id=report_id, workspace_id=workspace.id)
    return ReportOut.model_validate(report)


@router.get("/{report_id}/export/markdown")
async def export_report_markdown(
    report_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Export report content as raw Markdown download."""
    report = await ReportService.get_report(db=db, report_id=report_id, workspace_id=workspace.id)
    return Response(
        content=report.markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.md"}
    )


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Delete a report."""
    await ReportService.delete_report(db=db, report_id=report_id, workspace_id=workspace.id)
    return {"message": "Report deleted successfully"}
