import asyncio
import os

from starlette.websockets import WebSocketDisconnect

from src.core.config import settings
from src.infrastructure.storage.fs_tests import get_progress
from src.application.services.test_events import get_events_since


async def safe_ws_progress(websocket, test_id: str):
    await websocket.accept()
    cursor = 0

    try:
        while True:
            # Source of truth is the filesystem; recompute each tick.
            if not os.path.exists(os.path.join(settings.STORAGE, test_id)):
                await websocket.send_json({"error": "Test not found"})
                await asyncio.sleep(2)
                continue

            progress = get_progress(test_id)
            events, cursor = await get_events_since(test_id, cursor)
            await websocket.send_json(
                {
                    "type": "progress",
                    "progress": progress,
                    "events": [e.__dict__ for e in events],
                }
            )
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        # Client closed the connection — normal flow.
        return
    except asyncio.CancelledError:
        return