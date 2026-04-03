"""Configuração centralizada via variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do .env."""

    app_name: str = "Litrão no Preço Bom - API"
    debug: bool = False

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://litrao_user:changeme@postgres:5432/litrao"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Cache TTL em segundos (1 hora)
    cache_ttl: int = 3600

    # Paginação
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Singleton das configurações."""
    return Settings()
