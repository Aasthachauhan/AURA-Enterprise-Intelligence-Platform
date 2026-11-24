# AURA REST API Documentation

## 1. Overview & Base URL

The AURA backend exposes a comprehensive RESTful API built with FastAPI.
- **Base URL**: `http://127.0.0.1:8000/api/v1`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
- **Raw OpenAPI JSON Specification**: `http://127.0.0.1:8000/openapi.json`
- **Authentication**: Bearer Token in HTTP header: `Authorization: Bearer <jwt_access_token>`.

---

## 2. API Endpoint Groups Summary

The API is partitioned into 14 functional route groups:

| Route Group | Base Path | Description |
|---|---|---|
| **1. Authentication** | `/api/v1/auth` | User registration, login, token refresh, and profile inspection. |
| **2. Users** | `/api/v1/users` | User management and account profile updates. |
| **3. Workspaces** | `/api/v1/workspaces` | Workspace creation, listing, membership, and RBAC management. |
| **4. Documents** | `/api/v1/documents` | Multi-format upload, status tracking, chunk preview, and deletion. |
| **5. Retrieval** | `/api/v1/retrieval` | Hybrid RAG search (Dense + BM25 + RRF) and cross-encoder reranking. |
| **6. Agents** | `/api/v1/agents` | Multi-agent execution runs, subtask inspection, and human approval. |
| **7. Chat** | `/api/v1/chat` | Conversation sessions, message history, and real-time SSE streaming. |
| **8. Reports** | `/api/v1/reports` | Multi-format report generation, inspection, and Markdown export. |
| **9. Workflows** | `/api/v1/workflows` | Autonomous enterprise workflow catalog and execution runner. |
| **10. Evaluation** | `/api/v1/evaluation` | RAGAS / DeepEval benchmarking, metric evaluation, and dataset runs. |
| **11. Knowledge Base** | `/api/v1/knowledge-base` | Entity and relation graph discovery, search, and graph visualizer data. |
| **12. Analytics** | `/api/v1/analytics` | Real database operational metrics, latency percentiles, and costs. |
| **13. MCP** | `/api/v1/mcp` | Model Context Protocol tool discovery, server status, and tool calling. |
| **14. Health** | `/health` | Application health checks, system status, and diagnostics. |

---

## 3. Detailed Endpoint Reference

### 3.1 Authentication (`/api/v1/auth`)

#### `POST /api/v1/auth/register`
Creates a new user account with default membership.
- **Request Body**:
  ```json
  {
    "email": "user@aura.enterprise",
    "password": "SecurePassword123!",
    "full_name": "Jane Doe",
    "role": "admin"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "uuid-string",
    "email": "user@aura.enterprise",
    "full_name": "Jane Doe",
    "role": "admin",
    "is_active": true
  }
  ```

#### `POST /api/v1/auth/login`
Authenticates user credentials and issues JWT tokens.
- **Request Body**:
  ```json
  {
    "email": "user@aura.enterprise",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "uuid-string",
      "email": "user@aura.enterprise",
      "full_name": "Jane Doe",
      "role": "admin"
    }
  }
  ```

#### `POST /api/v1/auth/refresh`
Exchanges a valid refresh token for a fresh access token.
- **Request Body**: `{"refresh_token": "eyJhbGciOi..."}`
- **Response (200 OK)**: `{"access_token": "...", "token_type": "bearer"}`

#### `GET /api/v1/auth/me`
Returns current authenticated user details. Requires `Authorization: Bearer <token>`.

---

### 3.2 Documents (`/api/v1/documents`)

#### `POST /api/v1/documents/upload`
Uploads a document for ingestion, sanitization, chunking, and indexing.
- **Content-Type**: `multipart/form-data`
- **Parameters**: `file` (binary), `workspace_id` (string query parameter)
- **Response (201 Created)**:
  ```json
  {
    "id": "doc-uuid",
    "title": "sample_prd.docx",
    "file_type": "docx",
    "status": "indexed",
    "chunk_count": 8,
    "file_size_bytes": 38102,
    "created_at": "2026-11-24T06:50:00Z"
  }
  ```

#### `GET /api/v1/documents/?workspace_id={workspace_id}`
Returns all documents belonging to the workspace.

#### `GET /api/v1/documents/{document_id}/chunks`
Returns all indexed chunks for a document with page/sheet numbers and excerpts.

#### `DELETE /api/v1/documents/{document_id}`
Deletes a document and cascades deletion to all chunks and embeddings.

---

### 3.3 Hybrid Retrieval (`/api/v1/retrieval`)

#### `POST /api/v1/retrieval/search`
Executes hybrid search (Dense Embeddings + Okapi BM25 + Reciprocal Rank Fusion + Reranking).
- **Request Body**:
  ```json
  {
    "query": "What are the contractual SLA latency requirements?",
    "workspace_id": "ws-uuid",
    "top_k": 5
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "query": "What are the contractual SLA latency requirements?",
    "results": [
      {
        "chunk_id": "chunk-uuid",
        "document_title": "Enterprise SLA Agreement.pdf",
        "page_number": 3,
        "sheet_name": null,
        "content": "...99.95% uptime and sub-100ms P95 API response latency...",
        "rrf_score": 0.0328,
        "rerank_score": 0.89
      }
    ],
    "citations": ["[Enterprise SLA Agreement.pdf: Page 3]"]
  }
  ```

---

### 3.4 Multi-Agent Runs (`/api/v1/agents`)

#### `POST /api/v1/agents/run`
Launches the 7-agent LangGraph workflow for an enterprise task.
- **Request Body**:
  ```json
  {
    "workspace_id": "ws-uuid",
    "query": "Conduct PRD vs Test Coverage gap analysis and generate audit report",
    "conversation_id": "conv-uuid"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "run_id": "run-uuid",
    "status": "completed",
    "plan": ["Retrieve PRD specifications", "Retrieve test coverage matrix", "Compute gaps", "Synthesize report"],
    "subtasks": [...],
    "retry_count": 0,
    "verification_passed": true,
    "synthesized_answer": "...",
    "citations": [...]
  }
  ```

---

### 3.5 Real-Time Chat & SSE (`/api/v1/chat`)

#### `GET /api/v1/chat/stream?conversation_id={id}&message={text}&workspace_id={ws_id}`
Opens a Server-Sent Events (SSE) connection streaming token-by-token generation, agent execution steps, and grounded citations.

---

### 3.6 Reports (`/api/v1/reports`)

#### `POST /api/v1/reports/generate`
Generates a formal analytical report.
- **Request Body**:
  ```json
  {
    "workspace_id": "ws-uuid",
    "title": "Quarterly Financial Risk Audit",
    "report_type": "financial_audit",
    "format": "markdown"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "report-uuid",
    "title": "Quarterly Financial Risk Audit",
    "markdown_content": "# Quarterly Financial Risk Audit\n\n## Executive Summary\n...",
    "created_at": "2026-11-24T06:55:00Z"
  }
  ```

#### `GET /api/v1/reports/{report_id}/export?format=markdown`
Downloads the report as a clean `.md` file.

---

### 3.7 Autonomous Workflows (`/api/v1/workflows`)

#### `GET /api/v1/workflows/definitions`
Returns the catalog of registered business workflows:
- `prd_gap_analysis`: Product Requirements vs. Test Coverage Gap Analysis.
- `financial_audit`: Multi-Sheet Financial Variance & Discrepancy Audit.
- `contract_risk`: Master Services Agreement Risk & SLA Compliance Review.

#### `POST /api/v1/workflows/run`
Executes a selected workflow against specified document IDs.

---

### 3.8 Evaluation Benchmarks (`/api/v1/evaluation`)

#### `POST /api/v1/evaluation/run`
Executes RAGAS and DeepEval benchmarks over an evaluation dataset.
- **Request Body**: `{"workspace_id": "ws-uuid", "dataset_id": "eval-uuid", "run_name": "Weekly Regression"}`
- **Response (200 OK)**:
  ```json
  {
    "id": "eval-run-uuid",
    "faithfulness": 0.96,
    "answer_relevance": 0.94,
    "context_precision": 0.92,
    "context_recall": 0.90,
    "recall_at_k": 0.95,
    "citation_correctness": 0.98,
    "hallucination_rate": 0.04,
    "latency_avg_ms": 142
  }
  ```

---

### 3.9 Model Context Protocol (`/api/v1/mcp`)

#### `GET /api/v1/mcp/tools`
Lists all available MCP tools with their JSON Schema specifications.

#### `POST /api/v1/mcp/call`
Executes an MCP tool with provided parameters and records an audit log.

---

### 3.10 System Health (`/health`)

#### `GET /health`
Returns system status, active database connectivity, and uptime.
- **Response (200 OK)**: `{"status": "healthy", "version": "1.0.0", "database": "connected"}`
