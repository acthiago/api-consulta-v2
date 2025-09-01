"""Async wrapper to run index creation at startup if enabled."""
import asyncio

from scripts.migrations import m0001_create_indexes as m0001  # type: ignore


async def ensure_indexes() -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, m0001.run)
