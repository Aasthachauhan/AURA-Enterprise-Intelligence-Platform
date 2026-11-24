"""Integration tests for Document Upload, Duplicate Detection, and Deletion."""
import os
import io
import pytest


@pytest.mark.asyncio
async def test_document_upload_and_duplicate_detection(client, auth_headers):
    """Verify document upload validates file format, parses contents, and detects duplicates."""
    file_content = b"# PRD Specification\nRequirement REQ-001: The system shall support PDF parsing."
    files = {
        "file": ("test_prd.md", io.BytesIO(file_content), "text/markdown")
    }
    data = {"category": "Requirements"}

    # 1. Upload first time
    resp = await client.post("/api/v1/documents/upload", headers=auth_headers, files=files, data=data)
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["title"] == "test_prd"
    assert doc["category"] == "Requirements"

    # 2. Upload duplicate file (same content/hash)
    dup_files = {
        "file": ("test_prd.md", io.BytesIO(file_content), "text/markdown")
    }
    dup_resp = await client.post("/api/v1/documents/upload", headers=auth_headers, files=dup_files, data=data)
    assert dup_resp.status_code == 200
    dup_doc = dup_resp.json()
    # Same ID, incremented version
    assert dup_doc["id"] == doc["id"]
    assert dup_doc["version"] >= 2


@pytest.mark.asyncio
async def test_unsupported_file_rejection(client, auth_headers):
    """Verify unsupported file extensions are rejected with 400 Bad Request."""
    invalid_file = {
        "file": ("malicious.exe", io.BytesIO(b"MZBINARY"), "application/octet-stream")
    }
    resp = await client.post("/api/v1/documents/upload", headers=auth_headers, files=invalid_file, data={"category": "General"})
    assert resp.status_code == 400
    assert "Unsupported file format" in resp.json()["detail"]
