"""Predefined reproducible enterprise benchmark dataset."""
from typing import List, Dict, Any

STANDARD_BENCHMARK_SAMPLES: List[Dict[str, Any]] = [
    {
        "sample_id": "eval-01",
        "query": "What are the core system requirements and expected latency limits for the platform?",
        "ground_truth": "The platform requires response latency below 500ms for retrieval and 99.9% uptime SLA across all services.",
        "expected_docs": ["PRD", "System_Requirements", "Architecture"]
    },
    {
        "sample_id": "eval-02",
        "query": "Identify potential release risks and test coverage gaps in product requirement documents.",
        "ground_truth": "Missing automated tests for concurrency edge cases and lack of explicit rate limiting tests present high release risks.",
        "expected_docs": ["PRD", "Test_Coverage", "Risk_Assessment"]
    },
    {
        "sample_id": "eval-03",
        "query": "How is document authentication, authorization, and tenant isolation enforced?",
        "ground_truth": "Enforced via JWT Bearer tokens with RBAC (admin/member) and strict workspace/organization filtering on all database queries.",
        "expected_docs": ["Security_Spec", "Architecture"]
    },
    {
        "sample_id": "eval-04",
        "query": "What file types does the ingestion pipeline support and how are duplicates handled?",
        "ground_truth": "Supported formats include PDF, DOCX, XLSX, CSV, TXT, MD, and HTML. Duplicates are detected via SHA-256 file hashing.",
        "expected_docs": ["Ingestion_Guide", "Data_Pipeline"]
    },
    {
        "sample_id": "eval-05",
        "query": "Describe the multi-agent workflow and human-in-the-loop approval triggers.",
        "ground_truth": "Supervisor plans tasks and routes to Research, Document Intelligence, Analytical, Execution, and Verification agents. Irreversible or sensitive tools pause for human approval.",
        "expected_docs": ["Agent_Spec", "MCP_Integration"]
    }
]
