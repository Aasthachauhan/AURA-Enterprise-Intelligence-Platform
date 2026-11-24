"""Evaluation datasets and runs models."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Float
from app.core.database import Base


class EvalDataset(Base):
    __tablename__ = "eval_datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sample_count = Column(Integer, default=0)
    samples = Column(JSON, default=list)  # [{"query", "ground_truth", "expected_docs"}]
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("eval_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    model_name = Column(String(100), default="gpt-4o")
    status = Column(String(50), default="completed")  # "running", "completed", "failed"
    
    # RAGAS / DeepEval core metrics
    faithfulness = Column(Float, default=0.0)
    answer_relevance = Column(Float, default=0.0)
    context_precision = Column(Float, default=0.0)
    context_recall = Column(Float, default=0.0)
    retrieval_recall_at_k = Column(Float, default=0.0)
    citation_correctness = Column(Float, default=0.0)
    hallucination_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    
    detailed_results = Column(JSON, default=list)  # per-sample breakdown and failure logs
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
