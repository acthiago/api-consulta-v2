import json
from typing import Optional

import redis.asyncio as redis

from src.config.settings import Settings


class RedisCache:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: Optional[redis.Redis] = None

    async def connect(self) -> None:
        if not self._settings.CACHE_ENABLED:
            return
        if self._pool is None:
            self._pool = redis.from_url(
                self._settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def get_json(self, key: str) -> Optional[dict]:
        if not self._settings.CACHE_ENABLED or self._pool is None:
            return None
        data = await self._pool.get(key)
        return json.loads(data) if data else None

    async def set_json(self, key: str, value: dict, ttl: Optional[int] = None) -> None:
        if not self._settings.CACHE_ENABLED or self._pool is None:
            return
        ttl = ttl or self._settings.CACHE_TTL_SECONDS
        await self._pool.set(key, json.dumps(value), ex=ttl)

    async def delete(self, key: str) -> None:
        if not self._settings.CACHE_ENABLED or self._pool is None:
            return
        await self._pool.delete(key)
