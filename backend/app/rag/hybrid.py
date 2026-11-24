"""Hybrid retrieval combining dense vector search and BM25 with Reciprocal Rank Fusion."""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.vector_store import VectorStore
from app.rag.bm25 import bm25_index
from app.rag.embeddings import get_embedding_generator
from app.models.document import DocumentChunk


class RetrievedChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        document_title: str,
        content: str,
        page_number: Optional[int],
        sheet_name: Optional[str],
        section_title: Optional[str],
        score: float,
        vector_rank: Optional[int] = None,
        bm25_rank: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_title = document_title
        self.content = content
        self.page_number = page_number
        self.sheet_name = sheet_name
        self.section_title = section_title
        self.score = score
        self.vector_rank = vector_rank
        self.bm25_rank = bm25_rank
        self.metadata = metadata or {}


class HybridRetriever:
    def __init__(self, rrf_k: int = 60, alpha: float = 0.5):
        self.rrf_k = rrf_k
        self.alpha = alpha  # Weight between dense vector (alpha) and BM25 (1 - alpha)

    async def retrieve(
        self,
        db: AsyncSession,
        query: str,
        workspace_id: str,
        top_k: int = 5,
        filter_document_ids: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> List[RetrievedChunk]:
        """Execute hybrid search using Reciprocal Rank Fusion (RRF)."""
        # 1. Dense Vector Search
        embedder = get_embedding_generator()
        query_vec = await embedder.generate_embedding(query)
        vector_results = await VectorStore.search(
            db=db,
            query_vector=query_vec,
            workspace_id=workspace_id,
            top_k=top_k * 2,
            filter_document_ids=filter_document_ids,
            category=category
        )

        # 2. BM25 Search
        bm25_results = bm25_index.search(
            query=query,
            top_k=top_k * 2,
            workspace_id=workspace_id,
            filter_document_ids=filter_document_ids
        )

        # 3. Combine via Reciprocal Rank Fusion (RRF)
        # RRF_Score = 1 / (k + rank)
        combined_scores: Dict[str, float] = {}
        chunk_lookup: Dict[str, Any] = {}

        # Process Vector Results
        for rank, (chunk, v_score) in enumerate(vector_results):
            cid = chunk.id
            rrf_score = self.alpha * (1.0 / (self.rrf_k + rank + 1))
            combined_scores[cid] = combined_scores.get(cid, 0.0) + rrf_score
            chunk_lookup[cid] = {
                "chunk": chunk,
                "vector_rank": rank + 1,
                "bm25_rank": None
            }

        # Process BM25 Results
        for rank, (uid, bm25_score, meta) in enumerate(bm25_results):
            cid = meta.get("chunk_id")
            if not cid:
                continue
            rrf_score = (1.0 - self.alpha) * (1.0 / (self.rrf_k + rank + 1))
            combined_scores[cid] = combined_scores.get(cid, 0.0) + rrf_score
            if cid in chunk_lookup:
                chunk_lookup[cid]["bm25_rank"] = rank + 1
            else:
                chunk_lookup[cid] = {
                    "meta": meta,
                    "vector_rank": None,
                    "bm25_rank": rank + 1
                }

        # Sort by final combined RRF score
        sorted_cids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        retrieved: List[RetrievedChunk] = []
        for cid, score in sorted_cids:
            item = chunk_lookup[cid]
            if "chunk" in item:
                c = item["chunk"]
                doc = c.document
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=c.id,
                        document_id=doc.id if doc else c.document_id,
                        document_title=doc.title if doc else "Document",
                        content=c.content,
                        page_number=c.page_number,
                        sheet_name=c.sheet_name,
                        section_title=c.section_title,
                        score=score,
                        vector_rank=item["vector_rank"],
                        bm25_rank=item["bm25_rank"],
                        metadata=c.metadata_json or {}
                    )
                )
            elif "meta" in item:
                m = item["meta"]
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=cid,
                        document_id=m.get("document_id", ""),
                        document_title=m.get("document_title", "Document"),
                        content=m.get("text", ""),
                        page_number=m.get("page_number"),
                        sheet_name=m.get("sheet_name"),
                        section_title=m.get("section_title"),
                        score=score,
                        vector_rank=item["vector_rank"],
                        bm25_rank=item["bm25_rank"],
                        metadata=m
                    )
                )

        return retrieved
