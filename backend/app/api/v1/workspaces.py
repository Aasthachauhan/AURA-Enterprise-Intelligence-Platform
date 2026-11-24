"""Workspaces API router."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.core.database import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceOut
from app.models.workspace import Workspace, WorkspaceMember
from app.models.document import Document
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=List[WorkspaceOut])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all workspaces the authenticated user belongs to."""
    query = (
        select(Workspace)
        .join(WorkspaceMember)
        .filter(WorkspaceMember.user_id == current_user.id)
        .order_by(Workspace.created_at.desc())
    )
    result = await db.execute(query)
    workspaces = result.scalars().all()
    
    out = []
    for ws in workspaces:
        # Count documents
        doc_count_res = await db.execute(
            select(func.count(Document.id)).filter(Document.workspace_id == ws.id)
        )
        doc_count = doc_count_res.scalar() or 0
        out.append(
            WorkspaceOut(
                id=ws.id,
                organization_id=ws.organization_id,
                name=ws.name,
                description=ws.description,
                is_default=ws.is_default,
                created_at=ws.created_at,
                document_count=doc_count
            )
        )
    return out


@router.post("", response_model=WorkspaceOut)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new workspace and add current user as admin."""
    new_ws = Workspace(
        name=data.name,
        description=data.description,
        is_default=False
    )
    db.add(new_ws)
    await db.flush()
    
    member = WorkspaceMember(
        workspace_id=new_ws.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(member)
    await db.commit()
    await db.refresh(new_ws)
    
    return WorkspaceOut(
        id=new_ws.id,
        name=new_ws.name,
        description=new_ws.description,
        is_default=new_ws.is_default,
        created_at=new_ws.created_at,
        document_count=0
    )


@router.get("/{workspace_id}", response_model=WorkspaceOut)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get single workspace details."""
    query = (
        select(Workspace)
        .join(WorkspaceMember)
        .filter(Workspace.id == workspace_id, WorkspaceMember.user_id == current_user.id)
    )
    result = await db.execute(query)
    ws = result.scalars().first()
    if not ws:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        
    doc_count_res = await db.execute(
        select(func.count(Document.id)).filter(Document.workspace_id == ws.id)
    )
    doc_count = doc_count_res.scalar() or 0
    return WorkspaceOut(
        id=ws.id,
        organization_id=ws.organization_id,
        name=ws.name,
        description=ws.description,
        is_default=ws.is_default,
        created_at=ws.created_at,
        document_count=doc_count
    )
