"""Ponto de entrada da API FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app.routes.produtos import router as produtos_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Cria tabelas no startup e limpa no shutdown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=get_settings().app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos_router)


@app.get("/health")
async def health():
    """Healthcheck para o Docker."""
    return {"status": "ok"}
