# AURA System Design Specifications

## 1. Overview & Core Design Principles

AURA is engineered to meet enterprise requirements for predictability, zero-hallucination compliance, and auditability.
The platform adheres to four foundational design principles:
1. **Verifiable Truth**: Every generated claim must trace to a specific document chunk or database record. Unsupported statements are filtered or flagged.
2. **Deterministic Multi-Agent Coordination**: Agent workflows are structured as a finite state machine with strict input/output contracts rather than unpredictable autonomous loops.
3. **Multi-Tenant Isolation**: Every database entity, search vector, knowledge graph node, and chat session is scoped to a unique `workspace_id`.
4. **Observable Execution**: All LLM inferences, tool calls, and state transitions are recorded in real time and exposed through Server-Sent Events (SSE) and audit tables.

---

## 2. Sequence Diagrams

### 2.1 Authentication & Workspace Access
```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client
    participant AuthAPI as /api/v1/auth
    participant Security as Security Core (bcrypt & JWT)
    participant DB as Relational Database

    User->>AuthAPI: POST /login (email, password)
    AuthAPI->>DB: Query User by email
    DB-->>AuthAPI: User record (password_hash)
    AuthAPI->>Security: verify_password(plain, hashed)
    Security-->>AuthAPI: Validated (True)
    AuthAPI->>Security: create_access_token(user_id, role)
    AuthAPI->>Security: create_refresh_token(user_id)
    AuthAPI->>DB: Update last_login timestamp
    AuthAPI-->>User: 200 OK (access_token, refresh_token, user_profile)

    Note over User, AuthAPI: Subsequent requests include Authorization: Bearer <access_token>
    User->>AuthAPI: GET /api/v1/workspaces/
    AuthAPI->>DB: Query Workspaces where user_id in members
    DB-->>AuthAPI: List of authorized Workspaces
    AuthAPI-->>User: 200 OK (Workspaces)
```

---

### 2.2 Document Ingestion, Sanitization & Chunking
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Workspace Member
    participant DocAPI as /api/v1/documents
    participant Cleaner as Prompt Injection Sanitizer
    participant Parsers as Multi-Format Parsers
    participant Chunker as Recursive Semantic Chunker
    participant RAG as Dense & BM25 Indexer
    participant DB as Relational DB & Storage

    Admin->>DocAPI: POST /upload (file, workspace_id)
    DocAPI->>DB: Check duplicate SHA-256 hash
    alt Duplicate Found
        DocAPI-->>Admin: 409 Conflict (File already ingested)
    else Unique File
        DocAPI->>DB: Create Document(status="processing")
        DocAPI->>Parsers: parse_file(bytes, filename)
        Parsers-->>DocAPI: Raw text with page/sheet metadata
        DocAPI->>Cleaner: sanitize_text(raw_text)
        Cleaner-->>DocAPI: Sanitized text (injections stripped)
        DocAPI->>Chunker: chunk_text(sanitized_text, chunk_size=500, overlap=100)
        Chunker-->>DocAPI: List of chunks with metadata
        loop For each chunk
            DocAPI->>RAG: generate_embedding(chunk.content)
            RAG-->>DocAPI: 384-dimensional dense vector
            DocAPI->>DB: Insert DocumentChunk(content, embedding, page, sheet)
        end
        DocAPI->>RAG: update_bm25_index(workspace_id, chunks)
        DocAPI->>DB: Update Document(status="indexed", chunk_count=N)
        DocAPI-->>Admin: 201 Created (Document details)
    end
```

---

### 2.3 Hybrid Retrieval & Grounded Search
```mermaid
sequenceDiagram
    autonumber
    actor User as User / Agent
    participant RetAPI as /api/v1/retrieval
    participant DenseEngine as Semantic Vector Search
    participant SparseEngine as Okapi BM25 Index
    participant RRF as Reciprocal Rank Fusion
    participant Reranker as Cross-Encoder Reranker
    participant Citations as Citation Formatter
    participant DB as Database

    User->>RetAPI: POST /search (query, workspace_id, top_k=5)
    par Parallel Retrieval
        RetAPI->>DenseEngine: Search nearest neighbors (cosine similarity)
        DenseEngine->>DB: Fetch chunks by vector distance
        DB-->>DenseEngine: Top-M Dense candidates
    and
        RetAPI->>SparseEngine: Search BM25 inverted index (lexical match)
        SparseEngine-->>RetAPI: Top-M Sparse candidates
    end
    RetAPI->>RRF: Fuse candidates (alpha=0.5, k=60)
    RRF-->>RetAPI: Ranked fused candidate list
    RetAPI->>Reranker: Cross-Encoder score (lexical overlap + exact matches)
    Reranker-->>RetAPI: Final top-K ranked chunks
    RetAPI->>Citations: format_grounded_excerpts(chunks)
    Citations-->>RetAPI: Chunks with [DocTitle: Page X] attribution tags
    RetAPI-->>User: 200 OK (results, citations, confidence)
```

---

### 2.4 Multi-Agent LangGraph Orchestration Flow
```mermaid
sequenceDiagram
    autonumber
    actor Client as Chat Workspace / Workflow Runner
    participant Supervisor as Supervisor Agent
    participant Research as Research Agent
    participant DocIntel as Doc Intelligence Agent
    participant Analytical as Analytical Agent
    participant Execution as Execution Agent
    participant Verification as Verification Agent
    participant ReportGen as Report Generation Agent

    Client->>Supervisor: Initial query & workspace context
    Supervisor->>Supervisor: Decompose into subtasks & form plan
    Supervisor->>Research: Query context & gather evidence
    Research->>Research: Perform Hybrid RAG Search
    Research-->>Supervisor: Retrieved evidence chunks
    Supervisor->>DocIntel: Extract tables, entities & constraints
    DocIntel-->>Supervisor: Structured entity & tabular data
    Supervisor->>Analytical: Perform gap & risk analysis
    Analytical-->>Supervisor: Risk evaluation & compliance matrix
    opt Tool Calling Required
        Supervisor->>Execution: Execute MCP Tool (e.g. search_internal_knowledge)
        Execution-->>Supervisor: Tool execution output
    end
    Supervisor->>ReportGen: Synthesize findings into structured response
    ReportGen-->>Supervisor: Draft response with bracket citations
    Supervisor->>Verification: Verify claim-citation grounding
    alt Grounding Verification Failed (retry_count < 2)
        Verification-->>Supervisor: Hallucination detected / missing citations
        Supervisor->>Research: Re-retrieve missing evidence with refined query
    else Verification Succeeded or Fallback Reached
        Verification-->>Supervisor: Verified response + confidence score
        Supervisor-->>Client: Final grounded answer with citations
    end
```

---

## 3. Server-Sent Events (SSE) Protocol Specification

AURA streams live chat and workflow execution states using Server-Sent Events over HTTP at `/api/v1/chat/stream`.

### Event Types
| Event Type | Payload Schema | Description |
|---|---|---|
| `token` | `{"token": string}` | Emits partial LLM text tokens for real-time word-by-word UI rendering. |
| `agent_step` | `{"agent": string, "step": string, "status": "in_progress"\|"completed"}` | Notifies the frontend of active agent state transitions. |
| `tool_call` | `{"tool_name": string, "parameters": object, "status": string}` | Broadcasts MCP tool execution start and completion. |
| `citation` | `{"document_title": string, "page": number, "sheet": string, "snippet": string}` | Emits verified source citations as they are identified. |
| `final` | `{"message_id": string, "content": string, "citations": array, "confidence": number}` | Final message object concluding the stream. |
| `error` | `{"code": string, "message": string}` | Emitted if an unrecoverable exception occurs during execution. |

---

## 4. Multi-Tenant Isolation Strategy

```mermaid
graph TD
    subgraph Organization["Organization (Tenant Level)"]
        Org1["Organization ID: org-1234"]
        subgraph Workspace1["Workspace 1: Financial Audits"]
            W1_Docs["Documents & Vectors (workspace_id = ws-1)"]
            W1_Chats["Conversations (workspace_id = ws-1)"]
            W1_KG["Knowledge Graph (workspace_id = ws-1)"]
        end
        subgraph Workspace2["Workspace 2: Engineering PRDs"]
            W2_Docs["Documents & Vectors (workspace_id = ws-2)"]
            W2_Chats["Conversations (workspace_id = ws-2)"]
            W2_KG["Knowledge Graph (workspace_id = ws-2)"]
        end
    end

    UserMember["User (Role: Member in ws-1, No access to ws-2)"]
    UserMember -->|Can Access| Workspace1
    UserMember -.->|Blocked by RBAC / Tenant Filter| Workspace2
```

1. **Foreign Key Enforcement**: All core entities (`Document`, `DocumentChunk`, `Conversation`, `Message`, `AgentRun`, `KGEntity`, `Report`) hold a foreign key to `workspaces.id`.
2. **Query Scoping**: Every database select, update, and delete operation mandates a `.filter(Model.workspace_id == current_workspace_id)` clause.
3. **Vector Namespace Isolation**: Dense vector indices and BM25 inverted indices are sharded in memory and partitioned by `workspace_id`.
