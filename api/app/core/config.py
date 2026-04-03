"""Configuração centralizada via variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do .env."""

    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Litrão no Preço Bom - API"
    debug: bool = False

    # PostgreSQL
    database_url: str

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Cache TTL em segundos (1 hora)
    cache_ttl: int = 3600

    # CORS
    cors_origins: list[str] = ["http://localhost", "http://localhost:3000"]

    # Paginação
    default_page_size: int = 20
    max_page_size: int = 100


@lru_cache
def get_settings() -> Settings:
    """Singleton das configurações."""
    return Settings()
