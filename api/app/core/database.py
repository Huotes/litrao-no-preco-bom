"""Conexão assíncrona com PostgreSQL via SQLAlchemy."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

_settings = get_settings()
engine = create_async_engine(
    _settings.database_url,
    echo=_settings.debug,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa para todos os models."""


async def get_db():
    """Dependency injection de sessão do banco."""
    async with async_session() as session:
        yield session
