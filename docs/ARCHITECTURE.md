# AURA System Architecture

## 1. Executive Summary

AURA (Autonomous Enterprise Intelligence Platform) is an enterprise-grade AI system that unifies multi-format document ingestion, hybrid retrieval-augmented generation (RAG), multi-agent orchestration via LangGraph, Model Context Protocol (MCP) tool integration, and real-time business workflow execution.

The architecture is built from first principles to solve critical enterprise LLM challenges:
- **Hallucination Elimination**: Enforcing strict, verifiable bracket citations (`[DocTitle: Page X]`, `[DocTitle: Sheet Y]`) linked to source passages.
- **Explainable Agency**: Using a compiled LangGraph state machine with deterministic routing, human-in-the-loop checkpoints, and audit trails.
- **Standardized Tool Interoperability**: Adopting the Model Context Protocol (MCP) for tool registration, client-server separation, and telemetry.
- **Production Truthfulness**: Generating all metrics, latency percentiles, and operational dashboards from real database transactions without mock counters.

---

## 2. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client Layer (React 18 + Vite + Tailwind CSS)"]
        UI_Overview["Overview & KPI Dashboard"]
        UI_Chat["Chat Workspace (SSE Stream & Citations)"]
        UI_Docs["Document Ingestion & Chunk Inspector"]
        UI_Agents["Agent Monitor & Trace Visualizer"]
        UI_Workflows["Business Workflow Runner"]
        UI_KB["Knowledge Graph Visualizer"]
        UI_Reports["Report Generator & Markdown Viewer"]
        UI_Eval["Evaluation Benchmarks (RAGAS / DeepEval)"]
        UI_Analytics["Cost, Latency & Query Analytics"]
        UI_MCP["MCP Integration & Tool Tester"]
        UI_Settings["Settings & Security Policy"]
    end

    subgraph Gateway["API Gateway & Middleware Layer (FastAPI)"]
        CORS["CORS & Origin Validation"]
        JWT_Auth["JWT Authentication & RBAC Middleware"]
        TenantIso["Tenant & Workspace Isolation"]
        RateLimit["Rate Limiting & Request Throttling"]
        AuditLog["Tamper-Evident Audit Logging"]
    end

    subgraph CoreServices["Backend Application Core (Python 3.11 / FastAPI)"]
        AuthSvc["Authentication Service"]
        DocSvc["Document Ingestion & Cleaning Service"]
        ChatSvc["Chat & SSE Streaming Service"]
        ReportSvc["Report Synthesis Service"]
        WorkflowSvc["Autonomous Workflow Runner"]
        KGSvc["Knowledge Graph Extraction Service"]
        EvalSvc["Evaluation & Benchmark Engine"]
        AnalyticsSvc["Database Analytics Service"]
        MCPSvc["MCP Client & Tool Execution Service"]
    end

    subgraph HybridRAG["Hybrid RAG & Retrieval Engine"]
        Parsers["Multi-Format Parsers (PDF, DOCX, XLSX, CSV, HTML, TXT)"]
        Sanitizer["Prompt Injection Cleaner & Sanitizer"]
        Chunker["Recursive Overlapping Semantic Chunker"]
        BM25["Okapi BM25 Lexical Inverted Index"]
        Embedder["384-Dim Semantic Embedding Generator"]
        RRF["Reciprocal Rank Fusion (alpha=0.5, k=60)"]
        Reranker["Cross-Encoder Lexical Overlap Reranker"]
        CitationEngine["Strict Grounded Citation Validator"]
    end

    subgraph MultiAgentEngine["Multi-Agent Orchestration Layer (LangGraph)"]
        Supervisor["Supervisor Agent (Planning & Decomposition)"]
        Research["Research Agent (Hybrid RAG Retrieval)"]
        DocIntel["Document Intelligence Agent (Extraction)"]
        Analytical["Analytical Agent (Gap & Risk Analysis)"]
        Execution["Execution Agent (MCP Tool Invocation & Approval)"]
        ReportGen["Report Generation Agent (Synthesis)"]
        Verification["Verification Agent (Citation Alignment & Hallucination Guard)"]
    end

    subgraph MCPIntegration["Model Context Protocol (MCP) Ecosystem"]
        MCPServer["Local JSON-RPC 2.0 MCP Server"]
        MCPRegistry["Registered Enterprise Tools"]
        MCPClient["Sandboxed Async MCP Client"]
    end

    subgraph Persistence["Storage & Persistence Layer"]
        RelationalDB["Relational Database (SQLite / PostgreSQL)"]
        VectorDB["Vector Index (JSON Vectors / pgvector)"]
        FileStorage["Secure Local Object Storage (storage/)"]
    end

    %% Connections
    ClientLayer -->|REST & SSE (Bearer JWT)| Gateway
    Gateway --> CoreServices
    CoreServices --> MultiAgentEngine
    CoreServices --> HybridRAG
    CoreServices --> MCPIntegration
    CoreServices --> Persistence
    MultiAgentEngine --> HybridRAG
    MultiAgentEngine --> MCPIntegration
    HybridRAG --> Persistence
    MCPIntegration --> CoreServices
```

---

## 3. Subsystem Breakdown

### 3.1 Client Layer (Frontend SPA)
- Built with **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**.
- Pure client-side routing with React Router v6 across all 11 enterprise modules plus authentication.
- **Server-Sent Events (SSE)** client handling live token streams, agent step updates, tool execution traces, and citation metadata.
- Interactive **HTML5 Canvas Force-Directed Knowledge Graph** rendering entities and relations extracted from enterprise documents.
- Fully typed API client with automatic JWT token attachment, refresh interceptors, and error handling.

### 3.2 API Gateway & Security Layer
- Built on **FastAPI** with asynchronous request dispatch.
- **Authentication**: Stateless HMAC-SHA256 JWT access tokens paired with secure refresh tokens.
- **Role-Based Access Control (RBAC)**: Role validation (`admin`, `member`, `viewer`) enforced at route dependency levels.
- **Multi-Tenancy**: All database queries enforce strict filtering by `workspace_id` to prevent cross-tenant data leakage.
- **Security Sanitization**: Regex and heuristic filtering of incoming text to detect indirect prompt injections.

### 3.3 Hybrid RAG Pipeline
- **Parsers**: Dedicated extractors for PDF (`pypdf`), Word (`python-docx`), Excel (`openpyxl`), CSV, HTML (`beautifulsoup4`), and Markdown/Plain Text.
- **Chunker**: Recursive sliding-window chunker with 500-character windows, 100-character overlap, and metadata retention (`page_number`, `sheet_name`, `header_path`).
- **Dense Vector Search**: Deterministic 384-dimensional dense semantic embedding generator with cosine similarity ranking.
- **Sparse BM25 Index**: Okapi BM25 engine with inverted term indexing, stopword elimination, and dynamic inverse document frequency (IDF) calculation.
- **Hybrid Fusion**: Reciprocal Rank Fusion (RRF) combining dense and sparse ranks with parameter $k=60$ and $\alpha=0.5$.
- **Reranker**: Cross-encoder scoring based on exact phrase containment and entity overlap.
- **Citation Validator**: Verifies that every assertion cites a valid document chunk using `[DocTitle: Page X]` or `[DocTitle: Sheet Y]`.

### 3.4 Multi-Agent Orchestration (LangGraph)
- State machine implemented via LangGraph's `StateGraph`.
- Single shared immutable state passed across 7 purpose-built nodes.
- **Feedback & Retry Loop**: If the `VerificationAgent` flags claims without grounding or citation mismatch, control routes back to the `SupervisorAgent` with targeted feedback up to a configurable maximum retry limit (default 2), after which a graceful fallback is emitted.
- **Human-in-the-Loop**: High-consequence tool actions (e.g., executing changes or external API calls) pause in the `ExecutionAgent` pending administrative approval.

### 3.5 Model Context Protocol (MCP) Layer
- Follows the official Model Context Protocol JSON-RPC 2.0 specification over standard I/O and HTTP.
- Exposes 6 enterprise tools:
  1. `search_documents`: Vector + keyword search across workspace documents.
  2. `retrieve_document_sections`: Precise chunk fetching by document ID and index.
  3. `search_internal_knowledge`: Entity and relation discovery in the knowledge graph.
  4. `generate_report`: Automated report compilation.
  5. `query_application_data`: System and operational telemetry retrieval.
  6. `get_system_health`: Real-time system diagnostics.
- MCP client records all invocations in the `tool_executions` audit table.

### 3.6 Persistence & Data Storage
- **SQLAlchemy 2.0 Async Engine**: Fully non-blocking database queries with support for SQLite (development) and PostgreSQL + pgvector (production).
- **Physical File Storage**: Ingested files stored under UUID-partitioned storage trees with SHA-256 deduplication.

---

## 4. Scalability, Resilience & Fault Tolerance

| Aspect | Engineering Design |
|---|---|
| **Concurrency** | Asyncio event loop with async database sessions and non-blocking I/O. |
| **Deduplication** | Cryptographic SHA-256 hashing on file ingest prevents redundant chunking and embedding. |
| **Circuit Breaking** | Embeddings engine falls back gracefully from remote providers (OpenAI/Gemini) to deterministic local 384-dimensional vectors. |
| **Infinite Loop Guard** | Multi-agent state machine enforces `retry_count <= 2` in LangGraph verification edges. |
| **Database Transactions** | Unit of Work pattern via scoped async sessions with automatic rollback on unhandled exceptions. |
