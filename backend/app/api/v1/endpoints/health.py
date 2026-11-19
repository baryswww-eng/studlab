"""Liveness and database readiness checks."""

import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.database.session import get_session
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)


@router.get("", response_model=HealthResponse, summary="API liveness")
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get(
    "/db",
    response_model=DatabaseHealthResponse,
    summary="Database readiness",
    responses={503: {"model": DatabaseHealthResponse, "description": "Database unavailable"}},
)
async def health_db(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DatabaseHealthResponse | JSONResponse:
    start = time.perf_counter()
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        # Log the real cause server-side; do not leak connection details to clients.
        logger.warning("Database health check failed", exc_info=True)
        return JSONResponse(
            DatabaseHealthResponse(status="unavailable").model_dump(),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    latency = round((time.perf_counter() - start) * 1000, 2)
    return DatabaseHealthResponse(status="ok", latency_ms=latency)
