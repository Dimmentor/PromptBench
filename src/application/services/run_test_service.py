import asyncio
import os
import time

from src.core.logger import logger
from src.infrastructure.storage.fs_tests import (
    list_request_files,
    compute_request,
)


class RunTestService:
    def __init__(self, storage, llm_client):
        self.storage = storage
        self.llm_client = llm_client
        self.semaphore = asyncio.Semaphore(5)

    async def run(self, test_id: str):
        request_files = list_request_files(test_id)

        async def process(request_file_path: str):
            async with self.semaphore:
                req = compute_request(test_id, request_file_path)
                try:
                    payload = await self.storage.read_json(req.file_path)
                    start_time = time.time()
                    response = await self.llm_client.send(payload)
                    duration = int((time.time() - start_time) * 1000)

                    responses_dir = os.path.join(os.path.dirname(os.path.dirname(req.file_path)), "responses")
                    ok_path = os.path.join(responses_dir, f"response_{req.id}.json")
                    meta_path = os.path.join(responses_dir, f"response_{req.id}.meta.json")
                    err_path = os.path.join(responses_dir, f"response_{req.id}.error.json")

                    await self.storage.save_json(ok_path, response)
                    await self.storage.save_json(meta_path, {"duration": duration})
                    await self.storage.remove_file(err_path)
                except Exception as e:
                    responses_dir = os.path.join(os.path.dirname(os.path.dirname(req.file_path)), "responses")
                    err_path = os.path.join(responses_dir, f"response_{req.id}.error.json")
                    await self.storage.save_json(err_path, {"error": str(e)})

        await asyncio.gather(*(process(rf) for rf in request_files))

    async def run_with_status(self, test_id: str):
        from src.core.config import settings

        marker = os.path.join(settings.STORAGE, test_id, ".running")
        try:
            await self.storage.touch(marker)
            await self.run(test_id)
        except Exception as e:
            logger.exception(f"Run test failed: {e}")
        finally:
            await self.storage.remove_file(marker)