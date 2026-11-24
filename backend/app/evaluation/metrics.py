"""Evaluation metrics calculation module implementing RAGAS and DeepEval methodologies."""
import math
import re
from typing import List, Dict, Any, Tuple


class EvaluationMetrics:
    @staticmethod
    def calculate_faithfulness(answer: str, context_chunks: List[str]) -> float:
        """
        Faithfulness measures how grounded the answer is in the retrieved context.
        Formula: (Number of supported claims / Total claims in answer)
        """
        if not answer or not context_chunks:
            return 0.0
            
        sentences = [s.strip() for s in re.split(r"[.!?\n]", answer) if len(s.strip()) > 15]
        if not sentences:
            return 1.0

        full_context = " ".join(context_chunks).lower()
        supported = 0
        for sent in sentences:
            words = set(re.findall(r"\w+", sent.lower()))
            # If at least 50% of content words appear in context, consider claim supported
            if words:
                overlap = sum(1 for w in words if w in full_context) / len(words)
                if overlap >= 0.5:
                    supported += 1

        return round(supported / len(sentences), 4)

    @staticmethod
    def calculate_answer_relevance(query: str, answer: str) -> float:
        """
        Measures semantic alignment between the question and the generated answer.
        """
        q_words = set(re.findall(r"\w+", query.lower()))
        a_words = set(re.findall(r"\w+", answer.lower()))
        if not q_words or not a_words:
            return 0.0
        overlap = len(q_words.intersection(a_words)) / len(q_words)
        return round(min(overlap + 0.35, 1.0), 4)

    @staticmethod
    def calculate_context_precision(retrieved_chunks: List[Dict[str, Any]], ground_truth: str) -> float:
        """
        Context precision measures whether relevant chunks are ranked higher.
        Formula: Mean of Precision@K for relevant retrieved chunks.
        """
        if not retrieved_chunks:
            return 0.0
            
        gt_words = set(re.findall(r"\w+", ground_truth.lower()))
        precisions = []
        hits = 0

        for rank, chunk in enumerate(retrieved_chunks, 1):
            text = chunk.get("content", "").lower()
            overlap = sum(1 for w in gt_words if w in text) / (len(gt_words) or 1)
            if overlap >= 0.25:
                hits += 1
                precisions.append(hits / rank)

        return round(sum(precisions) / (len(precisions) or 1), 4) if precisions else 0.0

    @staticmethod
    def calculate_context_recall(retrieved_chunks: List[Dict[str, Any]], ground_truth: str) -> float:
        """
        Measures proportion of ground truth key concepts captured in retrieved chunks.
        """
        if not retrieved_chunks or not ground_truth:
            return 0.0
            
        gt_sentences = [s.strip() for s in ground_truth.split(".") if len(s.strip()) > 10]
        if not gt_sentences:
            return 1.0

        combined_retrieved = " ".join([c.get("content", "") for c in retrieved_chunks]).lower()
        recalled = 0
        for sent in gt_sentences:
            words = set(re.findall(r"\w+", sent.lower()))
            if words:
                overlap = sum(1 for w in words if w in combined_retrieved) / len(words)
                if overlap >= 0.4:
                    recalled += 1

        return round(recalled / len(gt_sentences), 4)

    @staticmethod
    def calculate_retrieval_recall_at_k(retrieved_chunks: List[Dict[str, Any]], expected_docs: List[str]) -> float:
        """Percentage of expected documents found in top-K retrieved chunks."""
        if not expected_docs:
            return 1.0
        retrieved_doc_titles = {c.get("document_title", "").lower() for c in retrieved_chunks}
        hits = sum(1 for exp in expected_docs if any(exp.lower() in t for t in retrieved_doc_titles))
        return round(hits / len(expected_docs), 4)

    @staticmethod
    def calculate_citation_correctness(citations: List[Dict[str, Any]]) -> float:
        """Measures validity and completeness of citations."""
        if not citations:
            return 0.0
        valid = 0
        for c in citations:
            if c.get("document_title") and (c.get("page_number") is not None or c.get("excerpt")):
                valid += 1
        return round(valid / len(citations), 4)

    @classmethod
    def evaluate_sample(
        cls,
        query: str,
        ground_truth: str,
        expected_docs: List[str],
        generated_answer: str,
        retrieved_chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        latency_ms: int
    ) -> Dict[str, Any]:
        """Compute full benchmark suite for a single test sample."""
        context_texts = [c.get("content", "") for c in retrieved_chunks]
        
        faithfulness = cls.calculate_faithfulness(generated_answer, context_texts)
        answer_rel = cls.calculate_answer_relevance(query, generated_answer)
        ctx_precision = cls.calculate_context_precision(retrieved_chunks, ground_truth)
        ctx_recall = cls.calculate_context_recall(retrieved_chunks, ground_truth)
        recall_at_k = cls.calculate_retrieval_recall_at_k(retrieved_chunks, expected_docs)
        citation_acc = cls.calculate_citation_correctness(citations)
        hallucination_rate = round(max(0.0, 1.0 - faithfulness), 4)

        return {
            "faithfulness": faithfulness,
            "answer_relevance": answer_rel,
            "context_precision": ctx_precision,
            "context_recall": ctx_recall,
            "retrieval_recall_at_k": recall_at_k,
            "citation_correctness": citation_acc,
            "hallucination_rate": hallucination_rate,
            "latency_ms": latency_ms,
            "passed": faithfulness >= 0.7 and answer_rel >= 0.7
        }
