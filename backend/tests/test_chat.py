"""Unit tests for Chat Workspace, Conversations, and Message Handling."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_conversation_lifecycle(client: AsyncClient, auth_headers: dict):
    """Test complete conversation lifecycle: create, list, fetch, update, delete."""
    # 1. Create conversation
    create_res = await client.post(
        "/api/v1/chat/conversations",
        headers=auth_headers,
        json={"title": "Q3 Enterprise Architecture Analysis"}
    )
    assert create_res.status_code in [200, 201]
    conv = create_res.json()
    conv_id = conv["id"]
    assert conv["title"] == "Q3 Enterprise Architecture Analysis"

    # 2. List conversations
    list_res = await client.get("/api/v1/chat/conversations", headers=auth_headers)
    assert list_res.status_code == 200
    conv_ids = [c["id"] for c in list_res.json()]
    assert conv_id in conv_ids

    # 3. Get single conversation
    get_res = await client.get(f"/api/v1/chat/conversations/{conv_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == conv_id
    assert "messages" in get_res.json()

    # 4. Update conversation (rename and pin)
    update_res = await client.patch(
        f"/api/v1/chat/conversations/{conv_id}",
        headers=auth_headers,
        json={"title": "Updated Architecture Analysis", "is_pinned": True}
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Architecture Analysis"
    assert update_res.json()["is_pinned"] is True

    # 5. Delete conversation
    del_res = await client.delete(f"/api/v1/chat/conversations/{conv_id}", headers=auth_headers)
    assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_chat_message_and_feedback(client: AsyncClient, auth_headers: dict):
    """Test sending user message, receiving agent response, and submitting feedback."""
    # Create conversation
    create_res = await client.post(
        "/api/v1/chat/conversations",
        headers=auth_headers,
        json={"title": "Test Chat Feedback"}
    )
    conv_id = create_res.json()["id"]

    # Post message
    msg_res = await client.post(
        f"/api/v1/chat/conversations/{conv_id}/messages",
        headers=auth_headers,
        json={
            "content": "What are our security compliance standards?",
            "use_agents": True
        }
    )
    assert msg_res.status_code == 200
    assistant_msg = msg_res.json()
    assert assistant_msg["role"] == "assistant"
    assert len(assistant_msg["content"]) > 0
    assert "citations_json" in assistant_msg
    assert "agent_steps_json" in assistant_msg

    # Submit feedback rating (thumbs up = 1)
    msg_id = assistant_msg["id"]
    fb_res = await client.post(
        f"/api/v1/chat/messages/{msg_id}/feedback",
        headers=auth_headers,
        json={"rating": 1, "notes": "Accurate response with verifiable citations"}
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["feedback_rating"] == 1
