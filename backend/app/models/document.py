"""Document and Document Chunk models."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # "pdf", "docx", "xlsx", "csv", "txt", "md", "html"
    file_size_bytes = Column(Integer, default=0)
    file_hash = Column(String(64), index=True, nullable=True)
    
    category = Column(String(100), default="General", index=True)
    status = Column(String(50), default="pending", index=True)  # "pending", "processing", "completed", "failed"
    error_message = Column(Text, nullable=True)
    
    version = Column(Integer, default=1)
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    metadata_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    uploader = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    clean_content = Column(Text, nullable=False)
    
    # Source attribution
    page_number = Column(Integer, nullable=True)
    sheet_name = Column(String(100), nullable=True)
    section_title = Column(String(255), nullable=True)
    
    # Embedding stored as JSON float array for universal DB compatibility (SQLite / Postgres)
    embedding_json = Column(JSON, nullable=True)
    token_count = Column(Integer, default=0)
    metadata_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="chunks")
