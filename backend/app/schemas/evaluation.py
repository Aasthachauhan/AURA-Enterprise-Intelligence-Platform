"""Evaluation and benchmark schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class EvalDatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    samples: List[Dict[str, Any]]  # [{"query": "...", "ground_truth": "...", "expected_docs": [...]}]


class EvalDatasetOut(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    sample_count: int
    samples: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class EvalRunCreate(BaseModel):
    dataset_id: str
    model_name: Optional[str] = "gpt-4o"


class EvalRunOut(BaseModel):
    id: str
    dataset_id: str
    workspace_id: str
    model_name: str
    status: str
    faithfulness: float
    answer_relevance: float
    context_precision: float
    context_recall: float
    retrieval_recall_at_k: float
    citation_correctness: float
    hallucination_rate: float
    avg_latency_ms: float
    detailed_results: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
