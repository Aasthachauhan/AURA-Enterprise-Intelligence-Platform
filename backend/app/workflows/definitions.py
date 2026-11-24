"""Enterprise business workflow templates and definitions."""
from typing import List, Dict, Any

PRECONFIGURED_WORKFLOWS: List[Dict[str, Any]] = [
    {
        "id": "wf-prd-gap",
        "name": "PRD vs Test Coverage Gap Analysis",
        "description": "Cross-examines product requirements against test plans and existing coverage to identify unverified requirements and release risks.",
        "category": "Quality Engineering",
        "required_inputs": [
            {"name": "document_ids", "type": "documents", "description": "Select PRD and Test Spec documents"}
        ],
        "steps": [
            "Document Text & Table Parsing",
            "Functional Requirement Extraction",
            "Test Suite Coverage Mapping",
            "Missing Requirement & Edge Case Gap Detection",
            "Risk Assessment & QA Report Generation"
        ],
        "estimated_duration": "10-20 seconds"
    },
    {
        "id": "wf-financial-audit",
        "name": "Financial Document & Balance Sheet Audit",
        "description": "Extracts tables, verifies mathematical consistency, detects metric anomalies, and generates compliance summaries.",
        "category": "Finance & Compliance",
        "required_inputs": [
            {"name": "document_ids", "type": "documents", "description": "Select Financial Spreadsheets or Reports"}
        ],
        "steps": [
            "Spreadsheet Sheet Extraction",
            "Numerical Value & Metric Aggregation",
            "Discrepancy Identification",
            "Executive Audit Brief Generation"
        ],
        "estimated_duration": "15-25 seconds"
    },
    {
        "id": "wf-contract-risk",
        "name": "Contract & Legal Risk Assessment",
        "description": "Compares multi-party contracts, highlights conflicting liability clauses, and outlines regulatory compliance exposure.",
        "category": "Legal & Risk",
        "required_inputs": [
            {"name": "document_ids", "type": "documents", "description": "Select Master Service Agreements or Contracts"}
        ],
        "steps": [
            "Clause & Term Extraction",
            "Cross-Document Comparison",
            "Conflicting Statement Identification",
            "Legal Risk Brief Generation"
        ],
        "estimated_duration": "12-22 seconds"
    }
]
