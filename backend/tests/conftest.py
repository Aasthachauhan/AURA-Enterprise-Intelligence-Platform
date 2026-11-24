"""Pytest fixtures and test configuration."""
import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.database import Base, get_db, init_db, engine, AsyncSessionLocal
from app.main import app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test tables across all engines."""
    import app.models  # noqa
    await init_db()
    yield


@pytest_asyncio.fixture
async def db_session():
    """Provide isolated db session for a test."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Provide HTTP test client with database override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register and log in a test user, returning authorization headers."""
    reg_data = {
        "email": "qa.engineer@enterprise.ai",
        "full_name": "QA Test Engineer",
        "password": "Password123!",
        "organization_name": "QA Lab Corp"
    }
    resp = await client.post("/api/v1/auth/register", json=reg_data)
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        ws_id = resp.json()["user"]["active_workspace_id"]
    else:
        # If user already exists, login
        login_res = await client.post("/api/v1/auth/login", json={"email": reg_data["email"], "password": reg_data["password"]})
        token = login_res.json()["access_token"]
        ws_id = login_res.json()["user"]["active_workspace_id"]

    return {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": ws_id
    }
