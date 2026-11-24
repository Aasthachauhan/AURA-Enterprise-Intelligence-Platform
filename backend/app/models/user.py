"""User and Organization models."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="member")  # "admin", "member", "analyst"
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    workspaces = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="uploader")
    conversations = relationship("Conversation", back_populates="user")
    reports = relationship("Report", back_populates="creator")
