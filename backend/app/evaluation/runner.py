"""Evaluation runner executing test batches and persisting run records."""
import time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.evaluation import EvalDataset, EvalRun
from app.evaluation.metrics import EvaluationMetrics
from app.evaluation.benchmark_dataset import STANDARD_BENCHMARK_SAMPLES
from app.rag.engine import rag_engine


class EvaluationRunner:
    @staticmethod
    async def seed_default_dataset(db: AsyncSession, workspace_id: str) -> EvalDataset:
        """Seed standard benchmark dataset if none exists in workspace."""
        res = await db.execute(select(EvalDataset).filter(EvalDataset.workspace_id == workspace_id))
        dataset = res.scalars().first()
        if not dataset:
            dataset = EvalDataset(
                workspace_id=workspace_id,
                name="Enterprise AI Core Benchmark Suite",
                description="Comprehensive evaluation dataset testing groundedness, citations, and hallucination defenses.",
                sample_count=len(STANDARD_BENCHMARK_SAMPLES),
                samples=STANDARD_BENCHMARK_SAMPLES
            )
            db.add(dataset)
            await db.commit()
            await db.refresh(dataset)
        return dataset

    @staticmethod
    async def run_evaluation(
        db: AsyncSession,
        dataset_id: str,
        workspace_id: str,
        model_name: str = "gpt-4o"
    ) -> EvalRun:
        """Execute full evaluation across all dataset samples and store metrics."""
        ds_res = await db.execute(select(EvalDataset).filter(EvalDataset.id == dataset_id))
        dataset = ds_res.scalars().first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        samples = dataset.samples or []
        detailed_results: List[Dict[str, Any]] = []

        total_faithfulness = 0.0
        total_answer_rel = 0.0
        total_ctx_precision = 0.0
        total_ctx_recall = 0.0
        total_recall_at_k = 0.0
        total_citation_acc = 0.0
        total_hallucination = 0.0
        total_latency = 0.0

        for sample in samples:
            query = sample.get("query", "")
            ground_truth = sample.get("ground_truth", "")
            expected_docs = sample.get("expected_docs", [])

            start = time.time()
            rag_output = await rag_engine.answer_query(
                db=db,
                query=query,
                workspace_id=workspace_id,
                top_k=5
            )
            lat_ms = int((time.time() - start) * 1000)

            sample_metrics = EvaluationMetrics.evaluate_sample(
                query=query,
                ground_truth=ground_truth,
                expected_docs=expected_docs,
                generated_answer=rag_output.get("answer", ""),
                retrieved_chunks=rag_output.get("retrieved_chunks", []),
                citations=rag_output.get("citations", []),
                latency_ms=lat_ms
            )

            sample_result = {
                "sample_id": sample.get("sample_id"),
                "query": query,
                "ground_truth": ground_truth,
                "generated_answer": rag_output.get("answer", "")[:300] + "...",
                "metrics": sample_metrics
            }
            detailed_results.append(sample_result)

            total_faithfulness += sample_metrics["faithfulness"]
            total_answer_rel += sample_metrics["answer_relevance"]
            total_ctx_precision += sample_metrics["context_precision"]
            total_ctx_recall += sample_metrics["context_recall"]
            total_recall_at_k += sample_metrics["retrieval_recall_at_k"]
            total_citation_acc += sample_metrics["citation_correctness"]
            total_hallucination += sample_metrics["hallucination_rate"]
            total_latency += lat_ms

        n = len(samples) or 1
        eval_run = EvalRun(
            dataset_id=dataset_id,
            workspace_id=workspace_id,
            model_name=model_name,
            status="completed",
            faithfulness=round(total_faithfulness / n, 4),
            answer_relevance=round(total_answer_rel / n, 4),
            context_precision=round(total_ctx_precision / n, 4),
            context_recall=round(total_ctx_recall / n, 4),
            retrieval_recall_at_k=round(total_recall_at_k / n, 4),
            citation_correctness=round(total_citation_acc / n, 4),
            hallucination_rate=round(total_hallucination / n, 4),
            avg_latency_ms=round(total_latency / n, 2),
            detailed_results=detailed_results
        )
        db.add(eval_run)
        await db.commit()
        await db.refresh(eval_run)

        return eval_run
