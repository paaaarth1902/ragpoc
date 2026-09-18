from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import health
from app.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = get_settings()
    yield

app = FastAPI(title="ragpoc",lifespan=lifespan)
app.include_router(health.router, tags=["health"])