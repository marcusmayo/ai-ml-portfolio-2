import asyncio
import json
from typing import Set

class ProgressManager:
    """Simple in-memory progress pub/sub using asyncio queues."""
    def __init__(self):
        self._subs: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        async with self._lock:
            self._subs.add(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue):
        async with self._lock:
            self._subs.discard(q)

    async def publish(self, payload: dict):
        # fan out without blocking the publisher
        async with self._lock:
            subs = list(self._subs)
        for q in subs:
            await q.put(payload)

    async def set(self, *, percent: int | None = None, message: str | None = None, stage: str | None = None):
        data = {}
        if percent is not None:
            data["percent"] = max(0, min(100, int(percent)))
        if message:
            data["message"] = message
        if stage:
            data["stage"] = stage
        await self.publish(data)
