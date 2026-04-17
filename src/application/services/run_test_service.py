import asyncio
import time

from src.core.database import SessionLocal
from src.core.logger import logger
from src.domain.enums import TestStatus
from src.infrastructure.repositories.request_repository import RequestRepository
from src.infrastructure.repositories.response_repository import ResponseRepository


class RunTestService:
    def __init__(self, test_repo, request_repo, storage, llm_client):
        self.test_repo = test_repo
        self.request_repo = request_repo
        self.storage = storage
        self.llm_client = llm_client
        self.semaphore = asyncio.Semaphore(5)

    async def run(self, test_id: int):
        requests = await self.test_repo.get_requests(test_id)

        async def process(req):
            async with self.semaphore:
                async with SessionLocal() as session:
                    request_repo = RequestRepository(session)
                    response_repo = ResponseRepository(session)

                    try:
                        payload = await self.storage.read_json(req.file_path)
                        start_time = time.time()
                        response = await self.llm_client.send(payload)
                        duration = int((time.time() - start_time) * 1000)  # Duration in milliseconds

                        # Use request ID for response file naming
                        response_file_name = f"response_{req.id}.json"
                        response_path = req.file_path.replace(f"request_{req.id}.json", response_file_name).replace("requests", "responses")
                        await self.storage.save_json(response_path, response)

                        # Save response to database
                        await response_repo.create(req.id, response_path, duration)

                        await request_repo.mark_done(req.id)

                    except Exception:
                        await request_repo.mark_failed(req.id)

        await asyncio.gather(*(process(r) for r in requests))

    async def run_with_status(self, test_id: int):
        try:
            await self.test_repo.set_status(test_id, TestStatus.RUNNING)
            await self.run(test_id)
            await self.test_repo.set_status(test_id, TestStatus.COMPLETED)
        except Exception as e:
            logger.exception(f"Run test failed: {e}")
            await self.test_repo.set_status(test_id, TestStatus.FAILED)