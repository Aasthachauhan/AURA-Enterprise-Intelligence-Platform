"""Document management API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.document import DocumentOut, DocumentChunkOut
from app.services.document_service import DocumentService
from app.ingestion.pipeline import run_ingestion_pipeline

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("General"),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process an individual document."""
    return await DocumentService.upload_document(
        db=db,
        file=file,
        workspace=workspace,
        user=current_user,
        category=category
    )


@router.post("/upload-batch", response_model=List[DocumentOut])
async def upload_batch_documents(
    files: List[UploadFile] = File(...),
    category: str = Form("General"),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process multiple documents simultaneously."""
    uploaded_docs = []
    for file in files:
        doc = await DocumentService.upload_document(
            db=db,
            file=file,
            workspace=workspace,
            user=current_user,
            category=category
        )
        uploaded_docs.append(doc)
    return uploaded_docs


@router.get("", response_model=dict)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    file_type: Optional[str] = None,
    status: Optional[str] = None,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List documents in workspace with search, filtering, and pagination."""
    if search in ("undefined", "null", ""):
        search = None
    if category in ("undefined", "null", "all", ""):
        category = None
    if file_type in ("undefined", "null", "all", ""):
        file_type = None
    if status in ("undefined", "null", "all", ""):
        status = None

    docs, total = await DocumentService.list_documents(
        db=db,
        workspace_id=workspace.id,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        file_type=file_type,
        status_filter=status
    )
    return {
        "items": [DocumentOut.model_validate(d) for d in docs],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve single document details."""
    docs, _ = await DocumentService.list_documents(db=db, workspace_id=workspace.id)
    doc = next((d for d in docs if d.id == document_id), None)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.get("/{document_id}/preview", response_model=List[DocumentChunkOut])
async def get_document_preview(
    document_id: str,
    limit: int = Query(10, ge=1, le=50),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Fetch structured chunk preview for a document."""
    chunks = await DocumentService.get_preview(
        db=db,
        document_id=document_id,
        workspace_id=workspace.id,
        max_chunks=limit
    )
    return [DocumentChunkOut.model_validate(c) for c in chunks]


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Trigger background reprocessing of a document."""
    background_tasks.add_task(run_ingestion_pipeline, document_id)
    return {"message": "Reprocessing initiated in background", "document_id": document_id}


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and all associated chunks."""
    await DocumentService.delete_document(db=db, document_id=document_id, workspace_id=workspace.id)
    return {"message": "Document deleted successfully"}
