"""
Health Check Router.

Provides a GET /api/v1/health endpoint that reports the
operational status of all system components: application,
database, cache, and AI model.

Used by:
  - Load balancers to check if the instance is healthy
  - Monitoring systems to detect outages
  - Developers to verify deployment status
"""

import logging
import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/api/v1", tags=["health"])
logger = logging.getLogger(__name__)

# Track application start time for uptime calculation
_start_time = time.time()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Return the operational status of all system components.

    Returns:
        200: All systems healthy
        Response includes: app info, database status, model status, uptime
    """

    # ── Database Check ───────────────────────────────────────
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"
        logger.error("Health check — database connection failed: %s", e)

    # ── Redis Check (placeholder until Redis is connected) ───
    redis_status = "not_configured"

    # ── AI Model Check ───────────────────────────────────────
    model_status = "enabled" if settings.MODEL_ENABLED else "disabled"

    # ── Uptime ───────────────────────────────────────────────
    uptime_seconds = round(time.time() - _start_time, 2)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
        },
        "components": {
            "database": db_status,
            "cache": redis_status,
            "ai_model": model_status,
        },
        "uptime_seconds": uptime_seconds,
    }
