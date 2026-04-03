"""Ponto de entrada da API FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.cache import close_redis
from app.core.config import get_settings
from app.core.database import engine
from app.routes.produtos import router as produtos_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup e shutdown da aplicação."""
    yield
    await close_redis()
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(produtos_router)


@app.get("/health")
async def health():
    """Healthcheck para o Docker."""
    return {"status": "ok"}
