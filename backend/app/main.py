"""Main FastAPI application entrypoint."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan handler."""
    logger.info("Initializing AURA Platform Database and Services...")
    await init_db()
    logger.info("AURA Platform ready.")
    yield
    logger.info("AURA Platform shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Full-Stack Generative AI, Agentic AI, RAG, MCP & Enterprise Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root platform status and documentation link."""
    return {
        "platform": settings.APP_NAME,
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }


@app.get("/health")
async def health():
    """Direct root health check."""
    return {"status": "healthy", "platform": settings.APP_NAME, "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Centralized exception handler ensuring standard structured error responses."""
    logger.error(f"Unhandled error on {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact the administrator."}
    )
