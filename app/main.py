from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import health
from app.db.session import engine
from app.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = get_settings()
    yield
    await engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(title="ragpoc", version="0.1.0", lifespan=lifespan)
    app.include_router(health.router, tags=["health"])
    return app

app = create_app()