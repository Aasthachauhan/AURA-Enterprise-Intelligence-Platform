"""Knowledge Graph extraction, relation linking, and graph exploration service."""
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.knowledge_graph import KGEntity, KGRelation
from app.models.document import Document, DocumentChunk


class KnowledgeGraphService:
    @staticmethod
    async def extract_and_index_document(
        db: AsyncSession,
        document_id: str,
        workspace_id: str
    ) -> int:
        """Extract entities and establish semantic relationships from document chunks."""
        chunk_res = await db.execute(
            select(DocumentChunk).filter(DocumentChunk.document_id == document_id)
        )
        chunks = chunk_res.scalars().all()
        if not chunks:
            return 0

        created_entities: List[KGEntity] = []

        for chunk in chunks:
            text = chunk.clean_content
            
            # Extract Organizations
            orgs = re.findall(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)\b", text)
            for org in orgs[:2]:
                if len(org) > 3 and org.lower() not in ["this", "that", "page", "table", "document"]:
                    e = KGEntity(
                        workspace_id=workspace_id,
                        document_id=document_id,
                        name=org,
                        entity_type="Organization",
                        description=f"Identified in document context: {text[:100]}...",
                        confidence=0.9
                    )
                    db.add(e)
                    created_entities.append(e)

            # Extract Requirements
            reqs = re.findall(r"(?:shall|must|should)\s+([^.\n]+)", text, re.IGNORECASE)
            for r in reqs[:2]:
                e = KGEntity(
                    workspace_id=workspace_id,
                    document_id=document_id,
                    name=r.strip()[:80],
                    entity_type="Requirement",
                    description=text[:120],
                    confidence=0.95
                )
                db.add(e)
                created_entities.append(e)

        await db.flush()

        # Link consecutive entities with relations
        for i in range(len(created_entities) - 1):
            rel = KGRelation(
                workspace_id=workspace_id,
                source_entity_id=created_entities[i].id,
                target_entity_id=created_entities[i + 1].id,
                relation_type="DEPENDS_ON" if created_entities[i].entity_type == "Requirement" else "ASSOCIATED_WITH",
                weight=1.0,
                evidence_text="Co-occurring in document context"
            )
            db.add(rel)

        await db.commit()
        return len(created_entities)

    @staticmethod
    async def get_graph(
        db: AsyncSession,
        workspace_id: str,
        limit_nodes: int = 50
    ) -> Dict[str, Any]:
        """Fetch nodes and edges for interactive Knowledge Graph visualization."""
        node_res = await db.execute(
            select(KGEntity).filter(KGEntity.workspace_id == workspace_id).limit(limit_nodes)
        )
        nodes = node_res.scalars().all()
        node_ids = {n.id for n in nodes}

        edges: List[Dict[str, Any]] = []
        if node_ids:
            rel_res = await db.execute(
                select(KGRelation).filter(
                    KGRelation.workspace_id == workspace_id,
                    KGRelation.source_entity_id.in_(node_ids),
                    KGRelation.target_entity_id.in_(node_ids)
                )
            )
            relations = rel_res.scalars().all()
            for r in relations:
                edges.append({
                    "id": r.id,
                    "source": r.source_entity_id,
                    "target": r.target_entity_id,
                    "relation": r.relation_type,
                    "weight": r.weight
                })

        return {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.entity_type,
                    "description": n.description,
                    "confidence": n.confidence
                }
                for n in nodes
            ],
            "edges": edges
        }
