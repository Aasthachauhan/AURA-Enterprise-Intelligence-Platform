"""Knowledge Base & Graph API router."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_workspace
from app.models.workspace import Workspace
from app.services.kg_service import KnowledgeGraphService

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


@router.get("/graph", response_model=Dict[str, Any])
async def get_knowledge_graph(
    limit: int = Query(60, ge=10, le=200),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Fetch nodes and edges for knowledge graph visualization."""
    return await KnowledgeGraphService.get_graph(
        db=db,
        workspace_id=workspace.id,
        limit_nodes=limit
    )


@router.post("/extract-all")
async def trigger_extraction_all(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Extract entities and establish graph relations from all processed workspace documents."""
    from sqlalchemy.future import select
    from app.models.document import Document
    res = await db.execute(select(Document).filter(Document.workspace_id == workspace.id, Document.status == "completed"))
    docs = res.scalars().all()
    total_count = 0
    for doc in docs:
        count = await KnowledgeGraphService.extract_and_index_document(
            db=db,
            document_id=doc.id,
            workspace_id=workspace.id
        )
        total_count += count
    return {"message": f"Successfully extracted {total_count} entities across {len(docs)} documents", "entities_extracted": total_count}


@router.post("/extract/{document_id}")
async def trigger_extraction(
    document_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Extract entities and establish graph relations from a document."""
    count = await KnowledgeGraphService.extract_and_index_document(
        db=db,
        document_id=document_id,
        workspace_id=workspace.id
    )
    return {"message": f"Successfully extracted {count} entities", "entities_extracted": count}
