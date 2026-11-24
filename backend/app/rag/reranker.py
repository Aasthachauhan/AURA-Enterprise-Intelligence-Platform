"""Cross-encoder style reranking and contextual relevance scoring."""
import re
from typing import List
from app.rag.hybrid import RetrievedChunk


class CrossEncoderReranker:
    @staticmethod
    def compute_lexical_overlap(query: str, text: str) -> float:
        """Compute exact token overlap and phrase matching."""
        q_tokens = set(re.findall(r"\w+", query.lower()))
        if not q_tokens:
            return 0.0
        t_tokens = set(re.findall(r"\w+", text.lower()))
        overlap = len(q_tokens.intersection(t_tokens)) / len(q_tokens)
        
        # Bonus if query phrase appears verbatim
        if query.lower() in text.lower():
            overlap += 0.3
        return min(overlap, 1.0)

    @classmethod
    def rerank(cls, query: str, chunks: List[RetrievedChunk], min_threshold: float = 0.01) -> List[RetrievedChunk]:
        """Rerank chunks based on cross-encoder scoring and contextual relevance."""
        reranked = []
        for chunk in chunks:
            overlap = cls.compute_lexical_overlap(query, chunk.content)
            # Combine initial retrieval score with lexical & phrase alignment
            final_score = (chunk.score * 0.6) + (overlap * 0.4)
            chunk.score = final_score
            if final_score >= min_threshold:
                reranked.append(chunk)

        reranked.sort(key=lambda x: x.score, reverse=True)
        return reranked
