"""Document Intelligence Agent: Entity, fact, requirement, and table extraction."""
import re
from typing import Dict, Any, List
from app.agents.state import AURAState


class DocumentIntelligenceAgent:
    @staticmethod
    async def run(state: AURAState) -> Dict[str, Any]:
        """Extract requirements, metrics, dates, and entities from evidence."""
        findings = state.get("research_findings", [])
        extracted_entities: List[Dict[str, Any]] = []

        for item in findings:
            text = item.get("evidence", "")
            source = item.get("source", "Document")
            
            # Extract requirement statements
            req_matches = re.findall(r"(?:shall|must|should|required to|needs to)\s+([^.\n]+)", text, re.IGNORECASE)
            for req in req_matches[:4]:
                extracted_entities.append({
                    "entity_type": "Requirement",
                    "name": req.strip()[:100],
                    "evidence": text[:200],
                    "source": source
                })
                
            # Extract numerical metrics / SLAs
            metric_matches = re.findall(r"(\d+(?:\.\d+)?\s*(?:%|ms|seconds|minutes|hours|GB|MB|USD|\$|users))", text, re.IGNORECASE)
            for met in metric_matches[:3]:
                extracted_entities.append({
                    "entity_type": "Metric",
                    "name": met.strip(),
                    "evidence": text[:150],
                    "source": source
                })

            # Extract Organizations / capitalized entities
            org_matches = re.findall(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b", text)
            for org in org_matches[:3]:
                if len(org) > 3 and org.lower() not in ["the", "this", "that", "page", "table", "section"]:
                    extracted_entities.append({
                        "entity_type": "Organization/Entity",
                        "name": org,
                        "evidence": text[:150],
                        "source": source
                    })

        plan_steps = state.get("plan_steps", [])
        for step in plan_steps:
            if step.get("agent") == "document_intelligence":
                step["status"] = "completed"

        return {
            "extracted_entities": extracted_entities,
            "plan_steps": plan_steps,
            "current_step_name": "Document Intelligence Completed"
        }
