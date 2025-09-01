import re
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.infra.cache.redis_cache import RedisCache


def normalize_cpf(cpf: str) -> str:
    return re.sub(r"[^\d]", "", cpf)


class ClienteRepository:
    def __init__(
        self, db: AsyncIOMotorDatabase, cache: Optional[RedisCache] = None
    ) -> None:
        self._db = db
        self._cache = cache

    async def get_by_cpf(self, cpf: str) -> Optional[dict]:
        key = f"cliente:cpf:{normalize_cpf(cpf)}"
        if self._cache:
            cached = await self._cache.get_json(key)
            if cached:
                return cached

        doc = await self._db.clientes.find_one({"cpf": normalize_cpf(cpf)})
        if doc and self._cache:
            # Convert ObjectId and datetime to string-safe values
            doc = self._serialize(doc)
            await self._cache.set_json(key, doc)
            return doc
        return self._serialize(doc) if doc else None

    def _serialize(self, doc: dict) -> dict:
        out = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                out[k] = str(v)
            elif hasattr(v, "isoformat"):
                out[k] = v.isoformat()
            else:
                out[k] = v
        return out
