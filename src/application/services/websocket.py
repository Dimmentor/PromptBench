import asyncio
import os

from starlette.websockets import WebSocketDisconnect

from src.core.config import settings
from src.infrastructure.storage.fs_tests import get_progress


async def safe_ws_progress(websocket, test_id: str):
    await websocket.accept()

    try:
        while True:
            # Source of truth is the filesystem; recompute each tick.
            if not os.path.exists(os.path.join(settings.STORAGE, test_id)):
                await websocket.send_json({"error": "Test not found"})
                await asyncio.sleep(2)
                continue

            await websocket.send_json(get_progress(test_id))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        # Client closed the connection — normal flow.
        return
    except asyncio.CancelledError:
        return