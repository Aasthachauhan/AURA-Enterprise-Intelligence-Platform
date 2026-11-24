"""Vector similarity store and search."""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.document import Document, DocumentChunk


class VectorStore:
    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two normalized vectors."""
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @classmethod
    async def search(
        cls,
        db: AsyncSession,
        query_vector: List[float],
        workspace_id: str,
        top_k: int = 10,
        filter_document_ids: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search document chunks by vector similarity."""
        query = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(Document.workspace_id == workspace_id, Document.status == "completed")
        )
        if filter_document_ids:
            query = query.filter(Document.id.in_(filter_document_ids))
        if category:
            query = query.filter(Document.category == category)

        result = await db.execute(query)
        rows = result.all()

        scored_chunks: List[Tuple[DocumentChunk, float]] = []
        for chunk, doc in rows:
            if not chunk.embedding_json:
                continue
            sim = cls.cosine_similarity(query_vector, chunk.embedding_json)
            # Store document reference on chunk for easy retrieval
            chunk.document = doc
            scored_chunks.append((chunk, sim))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]
