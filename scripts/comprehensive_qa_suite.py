"""Comprehensive End-to-End QA Validation Suite for AURA Platform.
Validates all 11 core modules against the live running backend API.
"""
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "http://127.0.0.1:8000/api/v1"

class QAResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.details = []

    def record(self, module: str, test_name: str, passed: bool, message: str = ""):
        if passed:
            self.passed += 1
            status = "PASS [OK]"
        else:
            self.failed += 1
            status = "FAIL [X]"
        line = f"[{status}] {module:<20} :: {test_name} - {message}"
        print(line)
        self.details.append({"module": module, "test": test_name, "passed": passed, "message": message})


def http_request(endpoint: str, method: str = "GET", data: dict = None, headers: dict = None, files: dict = None):
    url = f"{BASE_URL}{endpoint}"
    req_headers = headers.copy() if headers else {}
    
    if files:
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = bytearray()
        for field, (fname, fcontent, ftype) in files.items():
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{field}"; filename="{fname}"\r\n'.encode())
            body.extend(f"Content-Type: {ftype}\r\n\r\n".encode())
            body.extend(fcontent if isinstance(fcontent, bytes) else fcontent.encode())
            body.extend(b"\r\n")
        if data:
            for k, v in data.items():
                body.extend(f"--{boundary}\r\n".encode())
                body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
                body.extend(str(v).encode())
                body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())
        req_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        req_data = bytes(body)
    elif data is not None:
        req_headers["Content-Type"] = "application/json"
        req_data = json.dumps(data).encode("utf-8")
    else:
        req_data = None

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(raw.decode("utf-8"))
            return resp.status, raw.decode("utf-8")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            err_json = json.loads(raw.decode("utf-8"))
            return e.code, err_json
        except Exception:
            return e.code, raw.decode("utf-8", errors="ignore")
    except Exception as ex:
        return 500, {"error": str(ex)}


def run_full_qa():
    print("=" * 80)
    print("AURA PLATFORM - COMPREHENSIVE END-TO-END QA AUDIT")
    print(f"Target URL: {BASE_URL}")
    print(f"Timestamp:  {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 80)

    qa = QAResult()
    test_ts = int(time.time())
    qa_email = f"qa_auditor_{test_ts}@aura.enterprise"
    qa_password = "SecurePassword123!"

    # ==========================================
    # Module 1: Authentication & Authorization
    # ==========================================
    # 1.1 Register
    code, res = http_request("/auth/register", method="POST", data={
        "email": qa_email,
        "password": qa_password,
        "full_name": "QA Lead Auditor",
        "role": "admin"
    })
    qa.record("1. Authentication", "User Registration", code in [200, 201], f"Status: {code}")

    # 1.2 Login
    code, login_data = http_request("/auth/login", method="POST", data={
        "email": qa_email,
        "password": qa_password
    })
    token = login_data.get("access_token") if code == 200 else None
    refresh_token = login_data.get("refresh_token") if code == 200 else None
    qa.record("1. Authentication", "JWT Login", code == 200 and token is not None, f"Token received: {bool(token)}")

    if not token:
        print("[CRITICAL] Authentication failed. Aborting remaining tests.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1.3 Get Current User Profile
    code, me_data = http_request("/auth/me", headers=headers)
    qa.record("1. Authentication", "Get Profile (/auth/me)", code == 200 and me_data.get("email") == qa_email, f"Email: {me_data.get('email')}")

    # 1.4 Token Refresh
    code, ref_data = http_request("/auth/refresh", method="POST", data={"refresh_token": refresh_token})
    qa.record("1. Authentication", "Token Refresh", code == 200 and "access_token" in ref_data, "Refreshed access token successfully")

    # ==========================================
    # Module 2: Workspaces & Multi-Tenancy
    # ==========================================
    # 2.1 List Workspaces
    code, ws_list = http_request("/workspaces", headers=headers)
    qa.record("2. Workspaces", "List Workspaces", code == 200 and isinstance(ws_list, list) and len(ws_list) >= 1, f"Found {len(ws_list)} workspaces")

    current_ws_id = ws_list[0]["id"] if ws_list else None
    headers["X-Workspace-Id"] = current_ws_id

    # 2.2 Create Isolated Workspace
    code, new_ws = http_request("/workspaces", method="POST", headers=headers, data={
        "name": f"E2E Audit Workspace {test_ts}",
        "description": "Tenant isolated workspace for end-to-end verification"
    })
    qa.record("2. Workspaces", "Create Workspace", code in [200, 201] and "id" in new_ws, f"Created WS ID: {new_ws.get('id')}")
    audit_ws_id = new_ws.get("id") or current_ws_id
    headers["X-Workspace-Id"] = audit_ws_id

    # ==========================================
    # Module 3: Document Ingestion & Parsing
    # ==========================================
    # 3.1 Upload Markdown File
    md_content = """# System Security Specification
The AURA system implements AES-256 encryption at rest and TLS 1.3 in transit.
Session tokens expire after 24 hours of inactivity.
All API endpoints enforce tenant-level isolation via workspace header validation."""
    code, md_doc = http_request("/documents/upload", method="POST", headers=headers, 
                                files={"file": ("security_spec.md", md_content, "text/markdown")},
                                data={"category": "Security"})
    qa.record("3. Ingestion", "Upload Markdown Doc", code in [200, 201] and md_doc.get("status") == "completed", f"Doc ID: {md_doc.get('id')}, chunks: {md_doc.get('chunk_count')}")
    doc_id = md_doc.get("id")

    # 3.2 Upload CSV Data File
    csv_content = """Service,Tier,Latency_P99_ms,Target_Availability,Certified
Embedding_Service,Core,85,99.95%,Yes
Reranker_CrossEncoder,High,110,99.90%,Yes
Vector_Search_pgvector,Core,45,99.99%,Yes"""
    code, csv_doc = http_request("/documents/upload", method="POST", headers=headers,
                                 files={"file": ("slas.csv", csv_content, "text/csv")},
                                 data={"category": "Operations"})
    qa.record("3. Ingestion", "Upload CSV Metrics", code in [200, 201] and csv_doc.get("status") == "completed", f"Status: {csv_doc.get('status')}")

    # 3.3 List Workspace Documents
    code, doc_list = http_request("/documents", headers=headers)
    items = doc_list.get("items", []) if isinstance(doc_list, dict) else doc_list
    qa.record("3. Ingestion", "List Workspace Documents", code == 200 and len(items) >= 2, f"Total documents in workspace: {len(items)}")

    # 3.4 Document Preview & Chunks
    if doc_id:
        code, chunks = http_request(f"/documents/{doc_id}/preview", headers=headers)
        qa.record("3. Ingestion", "Preview Document Chunks", code == 200 and len(chunks) > 0, f"Retrieved {len(chunks)} chunks")

    # ==========================================
    # Module 4: Grounded RAG & Semantic Retrieval
    # ==========================================
    code, rag_res = http_request("/chat/conversations", method="POST", headers=headers, data={"title": "RAG QA Conversation"})
    conv_id = rag_res.get("id")
    qa.record("4. Grounded RAG", "Create Conversation", code in [200, 201] and conv_id is not None, f"Conv ID: {conv_id}")

    if conv_id:
        code, msg_res = http_request(f"/chat/conversations/{conv_id}/messages", method="POST", headers=headers, data={
            "content": "What encryption standard does AURA use for data at rest?",
            "use_agents": False
        })
        has_citations = len(msg_res.get("citations_json", [])) > 0 if code == 200 else False
        has_aes = "AES-256" in msg_res.get("content", "") if code == 200 else False
        qa.record("4. Grounded RAG", "Grounded Query Execution", code == 200 and has_aes, f"AES-256 identified: {has_aes}, Citations: {len(msg_res.get('citations_json', []))}")

    # ==========================================
    # Module 5: Conversational AI & Feedback
    # ==========================================
    if conv_id:
        # Multi-Agent Query
        code, agent_msg = http_request(f"/chat/conversations/{conv_id}/messages", method="POST", headers=headers, data={
            "content": "Compare our SLA latency requirements against vector search targets.",
            "use_agents": True
        })
        qa.record("5. Chat Workspace", "Multi-Agent Message Turn", code == 200 and len(agent_msg.get("content", "")) > 0, f"Steps: {len(agent_msg.get('agent_steps_json', []))}")

        # Submit Feedback
        msg_id = agent_msg.get("id")
        if msg_id:
            code, fb_res = http_request(f"/chat/messages/{msg_id}/feedback", method="POST", headers=headers, data={
                "rating": 1,
                "notes": "Verified accuracy against slas.csv"
            })
            qa.record("5. Chat Workspace", "Feedback Submission", code == 200 and fb_res.get("feedback_rating") == 1, f"Rating: {fb_res.get('feedback_rating')}")

    # ==========================================
    # Module 6: Autonomous Agents & Tool Tracking
    # ==========================================
    code, agent_runs = http_request("/agents/runs", headers=headers)
    qa.record("6. AI Agents", "List Agent Execution Runs", code == 200 and isinstance(agent_runs, list), f"Found {len(agent_runs)} agent runs")

    code, tool_execs = http_request("/agents/tools/executions", headers=headers)
    qa.record("6. AI Agents", "List Tool Executions", code == 200 and isinstance(tool_execs, list), f"Found {len(tool_execs)} tool logs")

    # ==========================================
    # Module 7: Autonomous Business Workflows
    # ==========================================
    code, workflows = http_request("/workflows", headers=headers)
    qa.record("7. Workflows", "List Workflow Templates", code == 200 and len(workflows) >= 3, f"Templates available: {len(workflows)}")

    if doc_id:
        code, wf_exec = http_request("/workflows/execute", method="POST", headers=headers, data={
            "workflow_id": "wf-prd-gap",
            "document_ids": [doc_id],
            "custom_instructions": "Prioritize encryption and security gaps"
        })
        qa.record("7. Workflows", "Execute PRD Gap Workflow", code == 200 and wf_exec.get("status") == "completed", f"Status: {wf_exec.get('status')}, Report: {wf_exec.get('report_title')}")

    # ==========================================
    # Module 8: Executive Reports
    # ==========================================
    if doc_id:
        code, rep_res = http_request("/reports", method="POST", headers=headers, data={
            "title": "AURA Executive Security Brief",
            "report_type": "security_brief",
            "document_ids": [doc_id],
            "query_or_focus": "Executive summary of cryptographic controls"
        })
        qa.record("8. Reports", "Generate Executive Report", code in [200, 201] and "id" in rep_res, f"Report ID: {rep_res.get('id')}")

    code, reports_list = http_request("/reports", headers=headers)
    qa.record("8. Reports", "List Executive Reports", code == 200 and len(reports_list) >= 1, f"Total reports: {len(reports_list)}")

    # ==========================================
    # Module 9: Knowledge Base & Knowledge Graph
    # ==========================================
    if doc_id:
        code, ext_res = http_request(f"/knowledge-base/extract/{doc_id}", method="POST", headers=headers)
        qa.record("9. Knowledge Base", "Trigger Entity Extraction", code == 200 and "entities_extracted" in ext_res, f"Entities extracted: {ext_res.get('entities_extracted')}")

    code, graph_data = http_request("/knowledge-base/graph", headers=headers)
    qa.record("9. Knowledge Base", "Query Knowledge Graph", code == 200 and "nodes" in graph_data, f"Nodes: {len(graph_data.get('nodes', []))}, Edges: {len(graph_data.get('edges', []))}")

    # ==========================================
    # Module 10: RAG Evaluations & Benchmarks
    # ==========================================
    code, eval_ds = http_request("/evaluations/datasets", method="POST", headers=headers, data={
        "name": f"Security Benchmark {test_ts}",
        "description": "Faithfulness and relevance test dataset",
        "samples": [
            {
                "query": "What encryption is used at rest?",
                "ground_truth": "AES-256 encryption at rest.",
                "contexts": ["The AURA system implements AES-256 encryption at rest."]
            }
        ]
    })
    qa.record("10. Evaluations", "Create Evaluation Dataset", code in [200, 201] and "id" in eval_ds, f"Dataset ID: {eval_ds.get('id')}")
    ds_id = eval_ds.get("id")

    if ds_id:
        code, eval_run = http_request("/evaluations/runs", method="POST", headers=headers, data={
            "dataset_id": ds_id,
            "model_name": "gpt-4o"
        })
        qa.record("10. Evaluations", "Trigger Evaluation Run", code in [200, 201] and "faithfulness" in eval_run, f"Faithfulness: {eval_run.get('faithfulness')}, Relevance: {eval_run.get('answer_relevance')}")

    # ==========================================
    # Module 11: Real Operational Analytics
    # ==========================================
    code, analytics = http_request("/analytics/overview", headers=headers)
    qa.record("11. Analytics", "Operational Overview Metrics", code == 200 and "total_documents" in analytics, f"Docs: {analytics.get('total_documents')}, Queue: {analytics.get('processing_queue_status')}")

    # ==========================================
    # Module 12: Model Context Protocol (MCP) Tools
    # ==========================================
    code, mcp_tools = http_request("/mcp/tools", headers=headers)
    qa.record("12. MCP Integration", "Discover MCP Tools", code == 200 and len(mcp_tools) >= 5, f"Tools registered: {len(mcp_tools)}")

    code, mcp_exec = http_request("/mcp/execute", method="POST", headers=headers, data={
        "tool_name": "get_system_health",
        "arguments": {}
    })
    qa.record("12. MCP Integration", "Execute Health Tool", code == 200 and mcp_exec.get("status") == "success", f"Status: {mcp_exec.get('status')}")

    code, mcp_app = http_request("/mcp/execute", method="POST", headers=headers, data={
        "tool_name": "query_application_data",
        "arguments": {"data_domain": "documents"}
    })
    qa.record("12. MCP Integration", "Execute App Data Tool", code == 200 and mcp_app.get("status") == "success", f"Status: {mcp_app.get('status')}")

    # Summary
    print("=" * 80)
    print(f"E2E QA AUDIT COMPLETE: {qa.passed} PASSED, {qa.failed} FAILED (Total: {qa.passed + qa.failed})")
    print(f"Success Rate: {(qa.passed / (qa.passed + qa.failed) * 100):.1f}%")
    print("=" * 80)

    if qa.failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_full_qa()
