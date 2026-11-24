"""Consolidated v1 API Router."""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.workspaces import router as workspaces_router
from app.api.v1.documents import router as documents_router
from app.api.v1.retrieval import router as retrieval_router
from app.api.v1.chat import router as chat_router
from app.api.v1.agents import router as agents_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.mcp import router as mcp_router
from app.api.v1.reports import router as reports_router
from app.api.v1.evaluation import router as eval_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.knowledge_base import router as kg_router
from app.api.v1.health import router as health_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(workspaces_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(retrieval_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(workflows_router)
api_v1_router.include_router(mcp_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(eval_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(kg_router)
api_v1_router.include_router(health_router)
