"""Tests for Embeddings, Vector Search, BM25, and Grounded RAG with Citations."""
import pytest
from app.rag.embeddings import DeterministicLocalEmbedder
from app.rag.bm25 import BM25Index
from app.rag.vector_store import VectorStore
from app.rag.reranker import CrossEncoderReranker
from app.rag.citations import CitationValidator
from app.rag.hybrid import RetrievedChunk


@pytest.mark.asyncio
async def test_deterministic_embedding_generator():
    """Verify embedding generator produces normalized vectors with semantic similarity."""
    embedder = DeterministicLocalEmbedder(dimension=384)
    v1 = await embedder.generate_embedding("latency constraints and response time SLAs")
    v2 = await embedder.generate_embedding("performance latency and response time limits")
    v3 = await embedder.generate_embedding("culinary recipes for chocolate cake")

    sim_related = VectorStore.cosine_similarity(v1, v2)
    sim_unrelated = VectorStore.cosine_similarity(v1, v3)

    assert len(v1) == 384
    assert sim_related > sim_unrelated
    assert sim_related > 0.4


def test_bm25_indexing_and_retrieval():
    """Verify BM25 keyword search ranks exact term matches."""
    idx = BM25Index()
    idx.add_document("doc1", "c1", "System requirements state latency shall be under 300ms", {"document_title": "PRD"})
    idx.add_document("doc2", "c2", "Budget spreadsheet allocates 150000 USD to AI research", {"document_title": "Financials"})

    results = idx.search("latency under 300ms", top_k=2)
    assert len(results) > 0
    assert "doc1:c1" in results[0][0]
    assert results[0][2]["document_title"] == "PRD"


def test_cross_encoder_reranker():
    """Verify CrossEncoderReranker boosts chunks with lexical and phrase overlap."""
    chunks = [
        RetrievedChunk("c1", "d1", "General Doc", "Generic information about technology.", None, None, None, 0.4),
        RetrievedChunk("c2", "d2", "PRD Doc", "System requirements specify 99.9% availability SLA.", None, None, None, 0.3)
    ]
    reranked = CrossEncoderReranker.rerank("99.9% availability SLA", chunks)
    assert len(reranked) == 2
    assert reranked[0].chunk_id == "c2"  # Boosted to top


def test_citation_validation():
    """Verify CitationValidator extracts and validates citations against context."""
    chunks = [
        RetrievedChunk("c1", "d1", "PRD.pdf", "Requirement REQ-001 specifies PDF and DOCX parsing.", 2, None, None, 0.9)
    ]
    generated_text = "As stated in [PRD.pdf: Page 2], the system supports PDF parsing."
    citations, score = CitationValidator.extract_and_verify_citations(generated_text, chunks)

    assert len(citations) == 1
    assert citations[0]["document_title"] == "PRD.pdf"
    assert citations[0]["page_number"] == 2
    assert score == 1.0
