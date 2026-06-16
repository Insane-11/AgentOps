import json
from typing import Any

from app.config import settings

try:
    import redis.asyncio as aioredis

    _redis: aioredis.Redis | None = aioredis.from_url(
        settings.redis_url or "redis://localhost:6379/0",
        decode_responses=True,
    )
except Exception:
    _redis = None


async def cache_get(key: str) -> Any | None:
    if not _redis:
        return None
    try:
        data = await _redis.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = 300):
    if not _redis:
        return
    try:
        await _redis.setex(key, ttl, json.dumps(value))
    except Exception:
        pass


async def cache_delete(key: str):
    if not _redis:
        return
    try:
        await _redis.delete(key)
    except Exception:
        pass


async def cache_invalidate_pattern(pattern: str):
    if not _redis:
        return
    try:
        keys = await _redis.keys(pattern)
        if keys:
            await _redis.delete(*keys)
    except Exception:
        pass
