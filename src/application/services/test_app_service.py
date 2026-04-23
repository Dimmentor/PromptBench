import asyncio
import os
from typing import Any, Callable

from src.application.exceptions import NotFoundError
from src.application.services.run_test_service import RunTestService
from src.core.config import settings
from src.infrastructure.storage.fs_index import unique_test_id, unique_request_id
from src.infrastructure.storage.fs_tests import (
    list_test_ids,
    list_request_files,
    compute_request,
    get_test_status,
    get_progress,
)


class TestApplicationService:
    """Use-cases for tests and request payloads backed by filesystem storage."""

    def __init__(
        self,
        storage: Any,
        llm_client_factory: Callable[[], Any],
    ):
        self._storage = storage
        self._llm_client_factory = llm_client_factory

    def _test_dir(self, test_id: str) -> str:
        return os.path.join(settings.STORAGE, test_id)

    def _require_test_dir(self, test_id: str) -> str:
        path = self._test_dir(test_id)
        if not os.path.exists(path):
            raise NotFoundError("Test not found")
        return path

    def _build_requests_view(self, test_id: str) -> list[dict[str, Any]]:
        requests: list[dict[str, Any]] = []
        for rf in list_request_files(test_id):
            req = compute_request(test_id, rf)
            resp = None
            if req.response_file_path:
                resp = {
                    "id": f"response_{req.id}",
                    "request_id": req.id,
                    "file_path": req.response_file_path,
                    "duration": req.duration,
                }
            requests.append(
                {
                    "id": req.id,
                    "test_id": test_id,
                    "file_path": req.file_path,
                    "status": req.status,
                    "response": resp,
                }
            )
        return requests

    def create_test(self, name: str) -> dict[str, Any]:
        os.makedirs(settings.STORAGE, exist_ok=True)
        test_id = unique_test_id(settings.STORAGE, name)
        test_dir = self._test_dir(test_id)
        os.makedirs(os.path.join(test_dir, "requests"), exist_ok=True)
        os.makedirs(os.path.join(test_dir, "responses"), exist_ok=True)
        return {
            "id": test_id,
            "name": test_id,
            "status": get_test_status(test_id),
            "requests": self._build_requests_view(test_id),
        }

    def get_test(self, test_id: str) -> dict[str, Any]:
        self._require_test_dir(test_id)
        return {
            "id": test_id,
            "name": test_id,
            "status": get_test_status(test_id),
            "requests": self._build_requests_view(test_id),
        }

    def list_tests(self) -> list[dict[str, Any]]:
        return [
            {"id": tid, "name": tid, "status": get_test_status(tid)}
            for tid in list_test_ids()
        ]

    @staticmethod
    def _next_request_id(requests_dir: str, data_name: str | None) -> str:
        if data_name is not None and str(data_name).strip() != "":
            base = "".join(
                ch if (ch.isalnum() or ch in ("_", "-")) else "_"
                for ch in data_name.strip()
            )
            base = base.strip("_") or "request"
            candidate = base
            i = 2
            while os.path.exists(os.path.join(requests_dir, f"{candidate}.json")):
                candidate = f"{base}_{i}"
                i += 1
            return candidate
        return unique_request_id()

    async def create_request(
        self,
        test_id: str,
        payload: dict[str, Any],
        name: str | None,
    ) -> dict[str, Any]:
        test_dir = self._require_test_dir(test_id)
        requests_dir = os.path.join(test_dir, "requests")
        os.makedirs(requests_dir, exist_ok=True)
        rid = self._next_request_id(requests_dir, name)
        file_path = os.path.join(requests_dir, f"{rid}.json")
        await self._storage.save_json(file_path, payload)
        return {"id": rid, "test_id": test_id, "file_path": file_path, "status": "pending"}

    async def delete_test(self, test_id: str) -> dict[str, str]:
        test_dir = self._require_test_dir(test_id)
        await self._storage.remove_tree(test_dir)
        return {"status": "deleted"}

    async def schedule_test_run(self, test_id: str) -> dict[str, str]:
        self._require_test_dir(test_id)
        service = RunTestService(self._storage, self._llm_client_factory())
        asyncio.create_task(service.run_with_status(test_id))
        return {"status": "started"}

    async def get_request_payload(
        self, test_id: str, request_id: str
    ) -> dict[str, Any]:
        self._require_test_dir(test_id)
        request_path = os.path.join(
            self._test_dir(test_id), "requests", f"{request_id}.json"
        )
        if not os.path.exists(request_path):
            raise NotFoundError("Request payload not found")
        data = await self._storage.read_json(request_path)
        return {
            "test_id": test_id,
            "request_id": request_id,
            "file_path": request_path,
            "payload": data,
        }

    async def save_request_payload(
        self, test_id: str, request_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        self._require_test_dir(test_id)
        request_path = os.path.join(
            self._test_dir(test_id), "requests", f"{request_id}.json"
        )
        if not os.path.exists(request_path):
            raise NotFoundError("Request payload not found")
        await self._storage.save_json(request_path, payload)
        return {
            "status": "saved",
            "test_id": test_id,
            "request_id": request_id,
            "file_path": request_path,
        }

    async def delete_request_payload(
        self, test_id: str, request_id: str
    ) -> dict[str, str]:
        self._require_test_dir(test_id)
        request_path = os.path.join(
            self._test_dir(test_id), "requests", f"{request_id}.json"
        )
        if not os.path.exists(request_path):
            raise NotFoundError("Request payload not found")
        await self._storage.remove_file(request_path)
        test_dir = self._test_dir(test_id)
        responses_dir = os.path.join(test_dir, "responses")
        for suffix in (".json", ".meta.json", ".error.json"):
            path = os.path.join(responses_dir, f"response_{request_id}{suffix}")
            await self._storage.remove_file(path)
        return {"status": "deleted", "test_id": test_id, "request_id": request_id}

    async def get_request_response(
        self, test_id: str, request_id: str
    ) -> dict[str, Any]:
        self._require_test_dir(test_id)
        responses_dir = os.path.join(self._test_dir(test_id), "responses")
        ok_path = os.path.join(responses_dir, f"response_{request_id}.json")
        meta_path = os.path.join(responses_dir, f"response_{request_id}.meta.json")
        err_path = os.path.join(responses_dir, f"response_{request_id}.error.json")

        ok = await self._storage.read_json(ok_path) if os.path.exists(ok_path) else None
        meta = (
            await self._storage.read_json(meta_path) if os.path.exists(meta_path) else None
        )
        err = await self._storage.read_json(err_path) if os.path.exists(err_path) else None

        if ok is None and meta is None and err is None:
            raise NotFoundError("Response not found")

        return {
            "test_id": test_id,
            "request_id": request_id,
            "ok_file_path": ok_path if os.path.exists(ok_path) else None,
            "meta_file_path": meta_path if os.path.exists(meta_path) else None,
            "error_file_path": err_path if os.path.exists(err_path) else None,
            "response": ok,
            "meta": meta,
            "error": err,
        }

    def get_progress(self, test_id: str) -> dict[str, int]:
        if not os.path.exists(self._test_dir(test_id)):
            raise NotFoundError("Test not found")
        return get_progress(test_id)
