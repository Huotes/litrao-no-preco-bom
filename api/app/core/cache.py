"""Utilitário de cache com Redis."""

import json
from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings

_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Retorna conexão Redis reutilizável."""
    global _pool  # noqa: PLW0603
    if _pool is None:
        _pool = redis.from_url(get_settings().redis_url, decode_responses=True)
    return _pool


async def cache_get(key: str) -> Any | None:
    """Busca valor do cache. Retorna None se não existir."""
    r = await get_redis()
    raw = await r.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    """Grava valor no cache com TTL opcional."""
    r = await get_redis()
    ttl = ttl if ttl is not None else get_settings().cache_ttl
    await r.set(key, json.dumps(value, default=str), ex=ttl)


async def cache_delete_pattern(pattern: str) -> None:
    """Remove chaves que casam com o padrão."""
    r = await get_redis()
    keys = [key async for key in r.scan_iter(match=pattern)]
    if keys:
        await r.delete(*keys)


async def close_redis() -> None:
    """Fecha a conexão Redis."""
    global _pool  # noqa: PLW0603
    if _pool is not None:
        await _pool.aclose()
        _pool = None
