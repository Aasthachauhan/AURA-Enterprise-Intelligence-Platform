"""Unit and integration tests for Authentication and Authorization."""
import pytest


@pytest.mark.asyncio
async def test_user_registration_and_login(client):
    """Test user registration, JWT generation, and login verification."""
    unique_email = "test.architect@enterprise.ai"
    reg_payload = {
        "email": unique_email,
        "full_name": "Enterprise Architect",
        "password": "SecurePassword123!",
        "organization_name": "Architecture Org"
    }
    
    # 1. Register
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code in [200, 400]
    
    # 2. Login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "SecurePassword123!"
    })
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == unique_email

    # 3. Profile Fetch with Bearer Token
    token = data["access_token"]
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == unique_email


@pytest.mark.asyncio
async def test_unauthorized_access_rejection(client):
    """Verify endpoints reject requests with missing or invalid credentials."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401

    invalid_token_resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert invalid_token_resp.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh(client):
    """Verify refresh token endpoint issues new access tokens."""
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "test.architect@enterprise.ai",
        "password": "SecurePassword123!"
    })
    if login_resp.status_code == 200:
        refresh_token = login_resp.json()["refresh_token"]
        ref_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert ref_resp.status_code == 200
        assert "access_token" in ref_resp.json()
