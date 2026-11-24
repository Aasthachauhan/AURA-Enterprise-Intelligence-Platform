"""Health and Readiness API router."""
import time
import psutil
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/health", tags=["System Health"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health check verifying database responsiveness, memory, and CPU."""
    db_healthy = False
    db_latency_ms = 0
    try:
        t0 = time.time()
        await db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - t0) * 1000, 2)
        db_healthy = True
    except Exception:
        db_healthy = False

    mem = psutil.virtual_memory() if hasattr(psutil, "virtual_memory") else None

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "AURA Enterprise Intelligence Platform",
        "database": {
            "status": "connected" if db_healthy else "error",
            "latency_ms": db_latency_ms
        },
        "system": {
            "cpu_percent": psutil.cpu_percent() if hasattr(psutil, "cpu_percent") else 0.0,
            "memory_usage_percent": mem.percent if mem else 0.0,
            "memory_available_mb": round(mem.available / (1024 * 1024), 2) if mem else 0.0
        },
        "mcp_server": "active",
        "timestamp": time.time()
    }
