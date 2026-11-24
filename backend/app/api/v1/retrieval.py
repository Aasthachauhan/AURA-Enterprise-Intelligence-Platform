"""Retrieval and Search API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_workspace
from app.models.workspace import Workspace
from app.rag.engine import rag_engine

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


@router.get("/search")
async def search_retrieval(
    q: str = Query(..., description="Query string to search"),
    top_k: int = Query(5, ge=1, le=20),
    category: Optional[str] = None,
    document_ids: Optional[List[str]] = Query(None),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Execute hybrid dense + BM25 search with cross-encoder reranking."""
    result = await rag_engine.answer_query(
        db=db,
        query=q,
        workspace_id=workspace.id,
        filter_document_ids=document_ids,
        category=category,
        top_k=top_k
    )
    return result
