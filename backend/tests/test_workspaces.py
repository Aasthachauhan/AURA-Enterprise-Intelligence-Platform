"""Unit tests for Multi-Tenant Workspaces, Isolation, and Membership."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_workspaces_crud_and_isolation(client: AsyncClient, auth_headers: dict):
    """Test workspace creation, listing, details inspection, and tenant isolation."""
    # 1. List user workspaces
    list_res = await client.get("/api/v1/workspaces", headers=auth_headers)
    assert list_res.status_code == 200
    ws_list = list_res.json()
    assert isinstance(ws_list, list)
    assert len(ws_list) >= 1

    # 2. Create new isolated workspace
    create_res = await client.post(
        "/api/v1/workspaces",
        headers=auth_headers,
        json={
            "name": "Financial Risk & Compliance Workspace",
            "description": "Isolated workspace for SOX and financial audits"
        }
    )
    assert create_res.status_code in [200, 201]
    new_ws = create_res.json()
    new_ws_id = new_ws["id"]
    assert new_ws["name"] == "Financial Risk & Compliance Workspace"

    # 3. Get workspace details
    get_res = await client.get(f"/api/v1/workspaces/{new_ws_id}", headers=auth_headers)
    assert get_res.status_code == 200
    ws_detail = get_res.json()
    assert ws_detail["id"] == new_ws_id
    assert ws_detail["name"] == "Financial Risk & Compliance Workspace"
    assert ws_detail["document_count"] == 0

    # 4. Cross-tenant isolation check: Attempt to access an invalid/foreign workspace
    foreign_res = await client.get(
        "/api/v1/workspaces/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": auth_headers["Authorization"], "X-Workspace-Id": "00000000-0000-0000-0000-000000000000"}
    )
    assert foreign_res.status_code in [403, 404]
