"""Evaluation API router."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models.user import User
from app.models.workspace import Workspace
from app.models.evaluation import EvalDataset, EvalRun
from app.schemas.evaluation import EvalDatasetCreate, EvalDatasetOut, EvalRunCreate, EvalRunOut
from app.evaluation.runner import EvaluationRunner

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.get("/datasets", response_model=List[EvalDatasetOut])
async def list_datasets(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List benchmark evaluation datasets in workspace."""
    # Ensure default dataset exists
    await EvaluationRunner.seed_default_dataset(db, workspace.id)
    res = await db.execute(select(EvalDataset).filter(EvalDataset.workspace_id == workspace.id))
    datasets = res.scalars().all()
    return [EvalDatasetOut.model_validate(d) for d in datasets]


@router.post("/datasets", response_model=EvalDatasetOut)
async def create_dataset(
    data: EvalDatasetCreate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Create a new custom evaluation dataset."""
    new_ds = EvalDataset(
        workspace_id=workspace.id,
        name=data.name,
        description=data.description,
        sample_count=len(data.samples),
        samples=data.samples
    )
    db.add(new_ds)
    await db.commit()
    await db.refresh(new_ds)
    return new_ds


@router.get("/runs", response_model=List[EvalRunOut])
async def list_evaluation_runs(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List past evaluation runs and benchmark histories."""
    res = await db.execute(
        select(EvalRun).filter(EvalRun.workspace_id == workspace.id).order_by(EvalRun.created_at.desc())
    )
    runs = res.scalars().all()
    return [EvalRunOut.model_validate(r) for r in runs]


@router.post("/runs", response_model=EvalRunOut)
async def trigger_evaluation_run(
    data: EvalRunCreate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a new automated evaluation run against a dataset."""
    return await EvaluationRunner.run_evaluation(
        db=db,
        dataset_id=data.dataset_id,
        workspace_id=workspace.id,
        model_name=data.model_name or "gpt-4o"
    )
