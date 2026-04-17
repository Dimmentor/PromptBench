import asyncio

from src.core.database import SessionLocal
from src.infrastructure.repositories.test_repository import TestRepository


async def safe_ws_progress(websocket, test_id: int):
    await websocket.accept()

    while True:
        async with SessionLocal() as session:
            repo = TestRepository(session)
            progress = await repo.get_progress(test_id)

        await websocket.send_json(progress)
        await asyncio.sleep(2)