"""Analytics API router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_workspace
from app.models.workspace import Workspace
from app.schemas.analytics import SystemMetricsOut
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=SystemMetricsOut)
async def get_overview_metrics(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve measured system analytics for dashboard visualization."""
    return await AnalyticsService.get_metrics(db=db, workspace_id=workspace.id)
