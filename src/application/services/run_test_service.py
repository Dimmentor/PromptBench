import asyncio
import os
import time

from src.core.logger import logger
from src.application.services.test_events import add_event
from src.infrastructure.storage.fs_tests import (
    list_request_files,
    compute_request,
    get_progress,
)


class RunTestService:
    def __init__(self, storage, llm_client):
        self.storage = storage
        self.llm_client = llm_client

    async def run(self, test_id: str):
        # Run strictly sequentially: orchestrator processes one request at a time,
        # and we want deterministic order + simpler progress reporting.
        request_files = sorted(list_request_files(test_id))

        for request_file_path in request_files:
            req = compute_request(test_id, request_file_path)
            try:
                await add_event(test_id, f"Обработка запрос {os.path.basename(req.file_path)}...")
                logger.info(f"[{test_id}] Обработка запрос {os.path.basename(req.file_path)}...")
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
                await add_event(
                    test_id,
                    f"Получен ответ на запрос {os.path.basename(req.file_path)}, сохранен в файл {os.path.basename(ok_path)}",
                )
                logger.info(
                    f"[{test_id}] Получен ответ на запрос {os.path.basename(req.file_path)}, сохранен в файл {os.path.basename(ok_path)}"
                )
            except Exception as e:
                responses_dir = os.path.join(os.path.dirname(os.path.dirname(req.file_path)), "responses")
                err_path = os.path.join(responses_dir, f"response_{req.id}.error.json")
                await self.storage.save_json(err_path, {"error": str(e)})
                await add_event(
                    test_id,
                    f"Ошибка при обработке {os.path.basename(req.file_path)}: {e}",
                    level="ERROR",
                )
                logger.error(f"[{test_id}] Ошибка при обработке {os.path.basename(req.file_path)}: {e}")

    async def run_with_status(self, test_id: str):
        from src.core.config import settings

        marker = os.path.join(settings.STORAGE, test_id, ".running")
        started = time.time()
        try:
            await add_event(test_id, f"Запуск теста {test_id}...")
            logger.info(f"[{test_id}] Запуск теста {test_id}...")
            await self.storage.touch(marker)
            await self.run(test_id)
        except Exception as e:
            logger.exception(f"Run test failed: {e}")
        finally:
            await self.storage.remove_file(marker)
            p = get_progress(test_id)
            total_duration_ms = int((time.time() - started) * 1000)
            summary = (
                f"Тест {test_id} обработан.\n"
                f"Успех: {p.get('done', 0)}, Ошибка: {p.get('failed', 0)}\n"
                f"Общее время: {total_duration_ms} ms"
            )
            await add_event(test_id, summary)
            logger.info(f"[{test_id}] {summary}")