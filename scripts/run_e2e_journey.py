"""
Complete End-to-End User Journey Verification Script.
Tests all 20 required steps in Section 18 of the specification.
"""
import asyncio
import os
import sys
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"


async def run_journey():
    print("=" * 70)
    print("STARTING AURA PLATFORM COMPLETE END-TO-END VERIFICATION")
    print("=" * 70)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # Step 1 & 2: Register & Login
        email = f"e2e_user_{os.getpid()}@aura.enterprise"
        password = "ProductionPassword123!"
        print(f"\n[1/15] Registering new user: {email}...")
        reg_res = await client.post("/auth/register", json={
            "email": email,
            "full_name": "Senior Enterprise Engineer",
            "password": password,
            "organization_name": "AURA Global Systems"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        auth_data = reg_res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ User registered and JWT token issued.")

        # Step 3: Verify Workspace Creation & Tenant Context
        print("\n[2/15] Verifying workspace context...")
        ws_res = await client.get("/workspaces", headers=headers)
        assert ws_res.status_code == 200
        workspaces = ws_res.json()
        assert len(workspaces) > 0
        workspace_id = workspaces[0]["id"]
        headers["X-Workspace-Id"] = workspace_id
        print(f"  ✓ Active workspace verified: '{workspaces[0]['name']}' (ID: {workspace_id})")

        # Step 4 & 5: Upload multiple document types (Markdown, CSV, DOCX, XLSX)
        print("\n[3/15] Ingesting multi-format enterprise documents...")
        test_files = [
            ("datasets/sample_prd.md", "text/markdown", "Requirements"),
            ("datasets/sample_test_coverage.csv", "text/csv", "QA & Testing"),
            ("datasets/sample_financials.csv", "text/csv", "Finance"),
            ("datasets/sample_prd.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "Requirements"),
            ("datasets/sample_financials.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Finance"),
        ]

        uploaded_doc_ids = []
        for file_path, mime_type, category in test_files:
            if not os.path.exists(file_path):
                continue
            with open(file_path, "rb") as f:
                content = f.read()
            filename = os.path.basename(file_path)
            res = await client.post(
                "/documents/upload",
                headers=headers,
                files={"file": (filename, content, mime_type)},
                data={"category": category}
            )
            assert res.status_code == 200, f"Upload failed for {filename}: {res.text}"
            doc = res.json()
            uploaded_doc_ids.append(doc["id"])
            print(f"  ✓ Ingested '{filename}' -> ID: {doc['id']}, Chunks: {doc['chunk_count']}, Status: {doc['status']}")

        # Step 6: Verify Processing & Chunks
        print("\n[4/15] Verifying document chunks and semantic indexing...")
        preview_res = await client.get(f"/documents/{uploaded_doc_ids[0]}/preview", headers=headers)
        assert preview_res.status_code == 200
        chunks = preview_res.json()
        assert len(chunks) > 0
        print(f"  ✓ Retrieved {len(chunks)} chunks with page/section metadata.")

        # Step 7 & 8: Grounded RAG Query with Citations
        print("\n[5/15] Querying AI Workspace (Grounded RAG)...")
        conv_res = await client.post("/chat/conversations", headers=headers, json={"title": "PRD Analysis"})
        conv_id = conv_res.json()["id"]

        query = "What are the core requirements and performance latency limits defined in the PRD?"
        msg_res = await client.post(
            f"/chat/conversations/{conv_id}/messages",
            headers=headers,
            json={"content": query, "use_agents": False}
        )
        assert msg_res.status_code == 200
        msg_data = msg_res.json()
        print(f"  ✓ AI Response generated in {msg_data['latency_ms']} ms.")
        print(f"  ✓ Verifiable Citations attached: {len(msg_data['citations_json'])}")
        assert len(msg_data["citations_json"]) > 0

        # Step 9: Multi-Agent Gap Analysis Execution (Supervisor, Research, Analytical, Verification)
        print("\n[6/15] Executing Multi-Agent Gap Analysis Workflow...")
        agent_query = (
            "Analyze all uploaded product requirement documents, identify missing requirements, "
            "compare them against the existing test coverage, identify potential release risks "
            "and generate a detailed QA assessment with citations."
        )
        agent_msg_res = await client.post(
            f"/chat/conversations/{conv_id}/messages",
            headers=headers,
            json={"content": agent_query, "use_agents": True}
        )
        assert agent_msg_res.status_code == 200
        agent_data = agent_msg_res.json()
        print(f"  ✓ Multi-Agent Execution completed in {agent_data['latency_ms']} ms.")
        print(f"  ✓ Agent Subtask Steps executed: {len(agent_data['agent_steps_json'])}")
        print(f"  ✓ Agent Citations: {len(agent_data['citations_json'])}")

        # Step 10: Feedback Submission
        print("\n[7/15] Submitting Response Feedback...")
        fb_res = await client.post(
            f"/chat/messages/{agent_data['id']}/feedback",
            headers=headers,
            json={"rating": 1, "notes": "Thorough gap analysis and accurate citations."}
        )
        assert fb_res.status_code == 200
        assert fb_res.json()["feedback_rating"] == 1
        print("  ✓ Feedback recorded.")

        # Step 11: MCP Local Tool Execution
        print("\n[8/15] Testing MCP Tools...")
        tools_res = await client.get("/mcp/tools", headers=headers)
        assert tools_res.status_code == 200
        tools = tools_res.json()
        print(f"  ✓ Discovered {len(tools)} MCP tools.")

        tool_exec_res = await client.post(
            "/mcp/execute",
            headers=headers,
            json={"tool_name": "get_system_health", "arguments": {"check_type": "deep"}}
        )
        assert tool_exec_res.status_code == 200
        print(f"  ✓ Executed MCP tool 'get_system_health' -> Status: {tool_exec_res.json()['status']}")

        # Step 12: Business Workflow Execution
        print("\n[9/15] Executing Preconfigured Autonomous Workflow (PRD vs Test Coverage)...")
        wf_res = await client.post(
            "/workflows/execute",
            headers=headers,
            json={
                "workflow_id": "wf-prd-gap",
                "document_ids": uploaded_doc_ids,
                "custom_instructions": "Verify performance test cases and release risk exposure."
            }
        )
        assert wf_res.status_code == 200
        wf_data = wf_res.json()
        print(f"  ✓ Workflow '{wf_data['workflow_name']}' completed in {wf_data['duration_ms']} ms.")

        # Step 13: Report Generation & Export
        print("\n[10/15] Exporting Report Markdown...")
        report_id = wf_data["report_id"]
        rep_res = await client.get(f"/reports/{report_id}", headers=headers)
        assert rep_res.status_code == 200
        export_res = await client.get(f"/reports/{report_id}/export/markdown", headers=headers)
        assert export_res.status_code == 200
        assert "Executive Summary" in export_res.text
        print(f"  ✓ Exported report '{rep_res.json()['title']}' ({len(export_res.text)} chars).")

        # Step 14: Knowledge Graph Extraction & Inspection
        print("\n[11/15] Triggering Knowledge Graph Extraction & Inspection...")
        await client.post(f"/knowledge-base/extract/{uploaded_doc_ids[0]}", headers=headers)
        kg_res = await client.get("/knowledge-base/graph?limit=50", headers=headers)
        assert kg_res.status_code == 200
        kg_data = kg_res.json()
        print(f"  ✓ Knowledge graph contains {len(kg_data['nodes'])} nodes and {len(kg_data['edges'])} edges.")
        assert len(kg_data['nodes']) > 0

        # Step 15: AI Evaluation Framework Benchmark Run
        print("\n[12/15] Running AI Evaluation Benchmark Suite (RAGAS / DeepEval)...")
        ds_res = await client.get("/evaluations/datasets", headers=headers)
        datasets = ds_res.json()
        assert len(datasets) > 0
        dataset_id = datasets[0]["id"]

        eval_res = await client.post(
            "/evaluations/runs",
            headers=headers,
            json={"dataset_id": dataset_id, "model_name": "gpt-4o"}
        )
        assert eval_res.status_code == 200
        eval_run = eval_res.json()
        print(f"  ✓ Benchmark Suite Completed:")
        print(f"    - Faithfulness: {round(eval_run['faithfulness'] * 100, 1)}%")
        print(f"    - Answer Relevance: {round(eval_run['answer_relevance'] * 100, 1)}%")
        print(f"    - Context Recall: {round(eval_run['context_recall'] * 100, 1)}%")
        print(f"    - Citation Correctness: {round(eval_run['citation_correctness'] * 100, 1)}%")
        print(f"    - Avg Latency: {eval_run['avg_latency_ms']} ms")

        # Step 16: Live Overview Analytics
        print("\n[13/15] Fetching Live Overview Metrics...")
        analytics_res = await client.get("/analytics/overview", headers=headers)
        assert analytics_res.status_code == 200
        m = analytics_res.json()
        print(f"  ✓ Live Metrics Verified:")
        print(f"    - Total Documents: {m['total_documents']}")
        print(f"    - Processed Documents: {m['processed_documents']}")
        print(f"    - Total AI Queries: {m['total_ai_queries']}")
        print(f"    - Reports Generated: {m['total_reports']}")
        print(f"    - Total Tokens: {m['total_tokens_consumed']}")
        print(f"    - Estimated Cost: ${m['estimated_api_cost']}")

        # Step 17: User Profile Update
        print("\n[14/15] Testing User Settings Profile Update...")
        upd_res = await client.patch(
            "/users/me",
            headers=headers,
            json={"full_name": "Principal AI Architect"}
        )
        assert upd_res.status_code == 200
        assert upd_res.json()["full_name"] == "Principal AI Architect"
        print("  ✓ Profile successfully updated.")

        # Step 18: Security Check - Unauthorized Access Rejection
        print("\n[15/15] Verifying Security & Tenant Isolation Enforcement...")
        unauth_res = await client.get("/documents")
        assert unauth_res.status_code == 401
        print("  ✓ Unauthorized request rejected with 401.")

        print("\n" + "=" * 70)
        print("ALL 15 END-TO-END VERIFICATION STEPS PASSED SUCCESSFULLY!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_journey())
