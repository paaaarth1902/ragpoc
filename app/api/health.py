""" Health probes - liveness and readiness probes """
from sqlalchemy import text
from typing import Any
from fastapi import Depends, APIRouter, Response, status
from app.config import Settings, get_settings
from app.db.session import engine

router = APIRouter()

@router.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {
        "status": "App is Healthy",
        "env": settings.app_env
    }

@router.get("/readyz")
async def readyz(response: Response) -> dict[str, Any]:
    checks: dict[str, str] = {}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # a readiness probe must report failure, never raise it
        checks["database"] = f"error: {type(exc).__name__}"

    ready = all(v == "ok" for v in checks.values())
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {"status": "ready" if ready else "not_ready", "checks": checks}