"""Tests for AI Evaluation Framework (RAGAS/DeepEval metrics)."""
import pytest
from app.evaluation.metrics import EvaluationMetrics


def test_faithfulness_metric():
    """Verify faithfulness metric detects grounded vs ungrounded claims."""
    context = [
        "The system SLA guarantees 99.9% uptime and p95 retrieval latency below 300ms."
    ]
    grounded_answer = "The platform delivers 99.9% uptime SLA with latency below 300ms."
    hallucinated_answer = "The platform is built using quantum computing chips running in Antarctica."

    faith_good = EvaluationMetrics.calculate_faithfulness(grounded_answer, context)
    faith_bad = EvaluationMetrics.calculate_faithfulness(hallucinated_answer, context)

    assert faith_good > 0.6
    assert faith_bad == 0.0


def test_answer_relevance_metric():
    """Verify answer relevance score increases with semantic alignment."""
    query = "What is the platform uptime SLA?"
    relevant_answer = "The platform SLA guarantees 99.9% system availability."
    irrelevant_answer = "The recipe requires two cups of flour and butter."

    rel_good = EvaluationMetrics.calculate_answer_relevance(query, relevant_answer)
    rel_bad = EvaluationMetrics.calculate_answer_relevance(query, irrelevant_answer)

    assert rel_good > rel_bad
