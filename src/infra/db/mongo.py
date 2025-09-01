from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.config.settings import Settings


class MongoProvider:
    """Manage a single Async MongoDB client and database instance."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = AsyncIOMotorClient(
                self._settings.MONGO_URI,
                minPoolSize=self._settings.MONGO_MIN_POOL_SIZE,
                maxPoolSize=self._settings.MONGO_MAX_POOL_SIZE,
                maxIdleTimeMS=self._settings.MONGO_MAX_IDLE_TIME_MS,
                uuidRepresentation="standard",
            )
            self._db = self._client[self._settings.MONGO_DB_NAME]

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("MongoProvider not connected")
        return self._db
