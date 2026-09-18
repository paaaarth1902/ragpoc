"""Health probe """

from fastapi import Depends, APIRouter
from app.config import Settings, get_settings

router = APIRouter()

@router.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {
        "status": "App is Healthy",
        "env": settings.app_env
    }
