import asyncio
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class TestEvent:
    ts_ms: int
    level: str
    message: str


_lock = asyncio.Lock()
_events: dict[str, list[TestEvent]] = {}


async def add_event(test_id: str, message: str, level: str = "INFO") -> None:
    ev = TestEvent(ts_ms=int(time.time() * 1000), level=level, message=message)
    async with _lock:
        arr = _events.setdefault(test_id, [])
        arr.append(ev)
        # keep memory bounded
        if len(arr) > 500:
            del arr[:200]


async def get_events_since(test_id: str, cursor: int) -> tuple[list[TestEvent], int]:
    async with _lock:
        arr = _events.get(test_id, [])
        if cursor < 0:
            cursor = 0
        if cursor > len(arr):
            cursor = len(arr)
        out = arr[cursor:]
        return out, len(arr)

