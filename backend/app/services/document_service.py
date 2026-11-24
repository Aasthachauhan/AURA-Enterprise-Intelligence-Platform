"""Document management service."""
import os
import uuid
import aiofiles
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_

from app.core.config import settings
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.models.workspace import Workspace
from app.models.audit import AuditLog
from app.ingestion.pipeline import run_ingestion_pipeline, compute_file_hash


class DocumentService:
    @staticmethod
    async def upload_document(
        db: AsyncSession,
        file: UploadFile,
        workspace: Workspace,
        user: User,
        category: str = "General"
    ) -> Document:
        """Validate, store, and enqueue document for ingestion."""
        # 1. Validate file extension
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if ext not in settings.ALLOWED_FILE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '.{ext}'. Allowed formats: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
            )

        # 2. Save file to disk
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        workspace_upload_dir = os.path.join(settings.UPLOAD_DIR, workspace.id)
        os.makedirs(workspace_upload_dir, exist_ok=True)
        file_path = os.path.join(workspace_upload_dir, unique_filename)

        file_size = 0
        content_bytes = await file.read()
        file_size = len(content_bytes)

        # Size check
        if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
            )

        with open(file_path, "wb") as f:
            f.write(content_bytes)

        # 3. Check for duplicates using hash
        file_hash = compute_file_hash(file_path)
        existing_doc_res = await db.execute(
            select(Document).filter(
                Document.workspace_id == workspace.id,
                Document.file_hash == file_hash
            )
        )
        existing_doc = existing_doc_res.scalars().first()
        if existing_doc:
            # Re-use existing or update version and reprocess
            existing_doc.version += 1
            existing_doc.status = "pending"
            await db.commit()
            await run_ingestion_pipeline(existing_doc.id)
            await db.refresh(existing_doc)
            return existing_doc

        # 4. Create Document record
        doc = Document(
            workspace_id=workspace.id,
            user_id=user.id,
            title=file.filename.rsplit(".", 1)[0],
            filename=file.filename,
            file_path=file_path,
            file_type=ext,
            file_size_bytes=file_size,
            file_hash=file_hash,
            category=category,
            status="pending",
            version=1
        )
        db.add(doc)
        await db.flush()

        audit = AuditLog(
            workspace_id=workspace.id,
            user_id=user.id,
            action="DOCUMENT_UPLOAD",
            resource_type="DOCUMENT",
            resource_id=doc.id,
            status="SUCCESS",
            details_json={"filename": file.filename, "size_bytes": file_size}
        )
        db.add(audit)
        await db.commit()
        await db.refresh(doc)

        # 5. Execute ingestion pipeline
        await run_ingestion_pipeline(doc.id)
        await db.refresh(doc)

        return doc

    @staticmethod
    async def list_documents(
        db: AsyncSession,
        workspace_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> Tuple[List[Document], int]:
        """List documents with pagination and multi-criteria filtering."""
        query = select(Document).filter(Document.workspace_id == workspace_id)

        if search:
            query = query.filter(
                or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.filename.ilike(f"%{search}%")
                )
            )
        if category and category != "all":
            query = query.filter(Document.category == category)
        if file_type and file_type != "all":
            query = query.filter(Document.file_type == file_type.lower())
        if status_filter and status_filter != "all":
            query = query.filter(Document.status == status_filter.lower())

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        # Paginated results
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        documents = result.scalars().all()

        return list(documents), total

    @staticmethod
    async def get_preview(
        db: AsyncSession,
        document_id: str,
        workspace_id: str,
        max_chunks: int = 10
    ) -> List[DocumentChunk]:
        """Fetch chunks for document preview."""
        doc_res = await db.execute(
            select(Document).filter(Document.id == document_id, Document.workspace_id == workspace_id)
        )
        doc = doc_res.scalars().first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        chunk_res = await db.execute(
            select(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .limit(max_chunks)
        )
        return list(chunk_res.scalars().all())

    @staticmethod
    async def reprocess(db: AsyncSession, document_id: str, workspace_id: str) -> bool:
        """Trigger reprocessing of a document."""
        doc_res = await db.execute(
            select(Document).filter(Document.id == document_id, Document.workspace_id == workspace_id)
        )
        doc = doc_res.scalars().first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        return await run_ingestion_pipeline(document_id)

    @staticmethod
    async def delete_document(db: AsyncSession, document_id: str, workspace_id: str) -> bool:
        """Delete document, chunks, and disk file."""
        doc_res = await db.execute(
            select(Document).filter(Document.id == document_id, Document.workspace_id == workspace_id)
        )
        doc = doc_res.scalars().first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass

        await db.delete(doc)
        await db.commit()
        return True
