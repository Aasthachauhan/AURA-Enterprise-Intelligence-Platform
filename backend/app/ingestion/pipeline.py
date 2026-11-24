"""Background document ingestion pipeline orchestration."""
import hashlib
import os
import traceback
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentChunk
from app.models.audit import AuditLog
from app.ingestion.parsers import DocumentParser
from app.ingestion.chunker import DocumentChunker
from app.rag.embeddings import get_embedding_generator
from app.rag.bm25 import bm25_index


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of a file for duplicate detection."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


async def run_ingestion_pipeline(document_id: str) -> bool:
    """
    Execute full ingestion lifecycle:
    Upload -> Validate -> Extract -> Clean -> Normalize -> Chunk -> Generate Embeddings -> Store -> Index -> Verify -> Complete.
    """
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Document).filter(Document.id == document_id))
            doc = result.scalars().first()
            if not doc:
                return False

            doc.status = "processing"
            doc.error_message = None
            await db.commit()

            if not os.path.exists(doc.file_path):
                raise FileNotFoundError(f"Source file not found at {doc.file_path}")

            # 1. Validate & Hash
            file_hash = compute_file_hash(doc.file_path)
            doc.file_hash = file_hash

            # 2. Extract / Parse
            sections = DocumentParser.parse(doc.file_path, doc.file_type)
            if not sections:
                raise ValueError("No extractable text content found in document")

            # 3. Chunking with overlap & source tracking
            chunker = DocumentChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
            chunk_items = chunker.chunk_sections(sections)
            if not chunk_items:
                raise ValueError("Document yielded 0 valid chunks after chunking")

            # 4. Generate Embeddings
            embedder = get_embedding_generator()
            chunk_texts = [c.clean_content for c in chunk_items]
            embeddings = await embedder.generate_embeddings_batch(chunk_texts)

            # 5. Clear any old chunks (for idempotency / reprocess)
            existing_chunks = await db.execute(select(DocumentChunk).filter(DocumentChunk.document_id == doc.id))
            for old_c in existing_chunks.scalars().all():
                await db.delete(old_c)
            await db.flush()

            # 6. Store Chunks & Update BM25 Index
            for c_item, emb in zip(chunk_items, embeddings):
                chunk_record = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=c_item.chunk_index,
                    content=c_item.content,
                    clean_content=c_item.clean_content,
                    page_number=c_item.page_number,
                    sheet_name=c_item.sheet_name,
                    section_title=c_item.section_title,
                    embedding_json=emb,
                    token_count=c_item.token_count,
                    metadata_json=c_item.metadata
                )
                db.add(chunk_record)
                
                # Add to in-memory / hybrid BM25 index
                bm25_index.add_document(
                    doc_id=doc.id,
                    chunk_id=chunk_record.id,
                    text=c_item.clean_content,
                    metadata={
                        "document_id": doc.id,
                        "document_title": doc.title,
                        "page_number": c_item.page_number,
                        "sheet_name": c_item.sheet_name,
                        "section_title": c_item.section_title,
                        "workspace_id": doc.workspace_id
                    }
                )

            # 7. Update Document status & metadata
            doc.status = "completed"
            doc.chunk_count = len(chunk_items)
            doc.page_count = max([c.page_number or 1 for c in chunk_items], default=1)
            doc.updated_at = datetime.now(timezone.utc)

            # Audit Log
            audit = AuditLog(
                workspace_id=doc.workspace_id,
                user_id=doc.user_id,
                action="DOCUMENT_INGESTION_COMPLETED",
                resource_type="DOCUMENT",
                resource_id=doc.id,
                status="SUCCESS",
                details_json={
                    "chunks": len(chunk_items),
                    "pages": doc.page_count,
                    "file_type": doc.file_type
                }
            )
            db.add(audit)

            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            error_trace = traceback.format_exc()
            
            # Record failure explicitly
            try:
                res = await db.execute(select(Document).filter(Document.id == document_id))
                failed_doc = res.scalars().first()
                if failed_doc:
                    failed_doc.status = "failed"
                    failed_doc.error_message = f"{str(e)}: {error_trace[:300]}"
                    
                    audit = AuditLog(
                        workspace_id=failed_doc.workspace_id,
                        user_id=failed_doc.user_id,
                        action="DOCUMENT_INGESTION_FAILED",
                        resource_type="DOCUMENT",
                        resource_id=failed_doc.id,
                        status="FAILURE",
                        details_json={"error": str(e)}
                    )
                    db.add(audit)
                    await db.commit()
            except Exception:
                pass
            return False
