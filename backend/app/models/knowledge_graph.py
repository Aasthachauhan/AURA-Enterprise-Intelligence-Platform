"""Knowledge Graph entities and relations models."""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Float
from app.core.database import Base


class KGEntity(Base):
    __tablename__ = "kg_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)  # "Person", "Organization", "Product", "Requirement", "Metric", "Date"
    description = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    metadata_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class KGRelation(Base):
    __tablename__ = "kg_relations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source_entity_id = Column(String(36), ForeignKey("kg_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_entity_id = Column(String(36), ForeignKey("kg_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relation_type = Column(String(100), nullable=False)  # "DEPENDS_ON", "IMPLEMENTS", "AUTHORED_BY", "CONTRADICTS", "VERIFIES"
    weight = Column(Float, default=1.0)
    evidence_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
