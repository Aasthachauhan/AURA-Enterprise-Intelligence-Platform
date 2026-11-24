# AURA Database Schema & Entity Design

## 1. Relational Database Overview

AURA utilizes an asynchronous SQLAlchemy 2.0 relational architecture with multi-tenant workspace isolation.
- **Local / Development Database**: SQLite with JSON vector storage via `aiosqlite`.
- **Production Database**: PostgreSQL 16 with native `pgvector` extension for vector similarity search.
- **Migration Strategy**: Fully declarative schema models with automated initialization via `Base.metadata.create_all`.

---

## 2. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ WORKSPACES : contains
    WORKSPACES ||--o{ WORKSPACE_MEMBERS : assigns
    USERS ||--o{ WORKSPACE_MEMBERS : joins
    WORKSPACES ||--o{ DOCUMENTS : owns
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : splits_into
    WORKSPACES ||--o{ CONVERSATIONS : scopes
    USERS ||--o{ CONVERSATIONS : initiates
    CONVERSATIONS ||--o{ MESSAGES : contains
    WORKSPACES ||--o{ AGENT_RUNS : executes
    AGENT_RUNS ||--o{ TOOL_EXECUTIONS : invokes
    WORKSPACES ||--o{ REPORTS : generates
    WORKSPACES ||--o{ EVAL_DATASETS : stores
    EVAL_DATASETS ||--o{ EVAL_RUNS : benchmarks
    WORKSPACES ||--o{ KG_ENTITIES : contains
    KG_ENTITIES ||--o{ KG_RELATIONS : source_relation
    KG_ENTITIES ||--o{ KG_RELATIONS : target_relation
    WORKSPACES ||--o{ AUDIT_LOGS : tracks

    USERS {
        string id PK
        string email UK
        string hashed_password
        string full_name
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ORGANIZATIONS {
        string id PK
        string name
        string slug UK
        datetime created_at
    }

    WORKSPACES {
        string id PK
        string organization_id FK
        string name
        string description
        datetime created_at
    }

    WORKSPACE_MEMBERS {
        string id PK
        string workspace_id FK
        string user_id FK
        string role
        datetime created_at
    }

    DOCUMENTS {
        string id PK
        string workspace_id FK
        string title
        string filename
        string file_type
        int file_size_bytes
        string storage_path
        string sha256_hash
        string status
        int chunk_count
        string error_message
        datetime created_at
        datetime updated_at
    }

    DOCUMENT_CHUNKS {
        string id PK
        string document_id FK
        string workspace_id FK
        int chunk_index
        text content
        int content_length
        int page_number
        string sheet_name
        string section_title
        text embedding_json
        int token_count
        datetime created_at
    }

    CONVERSATIONS {
        string id PK
        string workspace_id FK
        string user_id FK
        string title
        datetime created_at
        datetime updated_at
    }

    MESSAGES {
        string id PK
        string conversation_id FK
        string sender
        string role
        text content
        text citations_json
        text agent_steps_json
        int latency_ms
        int token_count
        datetime created_at
    }

    AGENT_RUNS {
        string id PK
        string workspace_id FK
        string user_id FK
        string conversation_id FK
        string workflow_name
        string status
        text plan_json
        text subtasks_json
        int retry_count
        boolean verification_passed
        int duration_ms
        datetime created_at
    }

    TOOL_EXECUTIONS {
        string id PK
        string agent_run_id FK
        string workspace_id FK
        string tool_name
        text parameters_json
        text result_json
        string status
        string error_message
        int duration_ms
        datetime created_at
    }

    REPORTS {
        string id PK
        string workspace_id FK
        string user_id FK
        string title
        string report_type
        string format
        text markdown_content
        text metadata_json
        datetime created_at
    }

    EVAL_DATASETS {
        string id PK
        string workspace_id FK
        string name
        string description
        int sample_count
        text samples_json
        datetime created_at
    }

    EVAL_RUNS {
        string id PK
        string workspace_id FK
        string dataset_id FK
        string run_name
        float faithfulness
        float answer_relevance
        float context_precision
        float context_recall
        float recall_at_k
        float citation_correctness
        float hallucination_rate
        int latency_avg_ms
        float cost_estimate
        text results_json
        datetime created_at
    }

    KG_ENTITIES {
        string id PK
        string workspace_id FK
        string document_id FK
        string name
        string entity_type
        string description
        text attributes_json
        datetime created_at
    }

    KG_RELATIONS {
        string id PK
        string workspace_id FK
        string source_entity_id FK
        string target_entity_id FK
        string relation_type
        float confidence
        text metadata_json
        datetime created_at
    }

    AUDIT_LOGS {
        string id PK
        string workspace_id FK
        string user_id FK
        string action
        string resource_type
        string resource_id
        string ip_address
        text details_json
        datetime created_at
    }
```

---

## 3. Detailed Table Specifications

### 3.1 `documents` & `document_chunks`
- **Duplicate Prevention**: The `documents.sha256_hash` column is indexed. Before processing, an incoming file's hash is compared against the workspace's ingested documents.
- **Chunk Metadata**: Every `document_chunks` record stores `page_number` (for PDFs and Word documents), `sheet_name` (for Excel workbooks), and `section_title` (for structured HTML and Markdown).
- **Vector Storage**:
  - In SQLite: Stored as serialized JSON string in `embedding_json` (384 float dimensions).
  - In PostgreSQL: Mapped to `vector(384)` with an HNSW cosine similarity index.

### 3.2 `agent_runs` & `tool_executions`
- Records full execution traces for explainability and auditing.
- `plan_json` captures the initial task breakdown produced by the `SupervisorAgent`.
- `subtasks_json` tracks execution state for each subtask.
- `tool_executions` captures tool name, invocation arguments, execution duration, and output payload.

### 3.3 `eval_datasets` & `eval_runs`
- Benchmarking tables storing real evaluations across RAGAS and DeepEval criteria.
- Metrics recorded: `faithfulness`, `answer_relevance`, `context_precision`, `context_recall`, `recall_at_k`, `citation_correctness`, and `hallucination_rate`.

### 3.4 `kg_entities` & `kg_relations`
- Backs the interactive Knowledge Base graph visualizer.
- Supports entity types: `system`, `metric`, `clause`, `component`, `feature`, `risk`, `actor`.
- Relations store directed edges with strength/confidence scores.

---

## 4. Indexing & Optimization Strategy

1. **Foreign Key Indexes**: All foreign keys (`workspace_id`, `document_id`, `conversation_id`, `agent_run_id`, etc.) are indexed to ensure sub-millisecond multi-tenant lookups.
2. **Composite Indexes**:
   - `(workspace_id, status)` on `documents` for rapid filtering of processing vs. indexed documents.
   - `(workspace_id, action, created_at)` on `audit_logs` for activity tracking and audit reports.
3. **Deduplication Index**:
   - `(workspace_id, sha256_hash)` on `documents` with unique constraint enforcement.
