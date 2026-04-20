import os
import asyncio
from fastapi import APIRouter, WebSocket, HTTPException

from src.application.services.websocket import safe_ws_progress
from src.core.config import settings
from src.infrastructure.storage.local import LocalStorageService
from src.infrastructure.storage.fs_index import unique_test_id, unique_request_id
from src.infrastructure.storage.fs_tests import (
    list_test_ids,
    list_request_files,
    compute_request,
    get_test_status,
    get_progress,
)
from src.infrastructure.llm.mock_client import MockLLMClient
from src.application.services.run_test_service import RunTestService
from src.interfaces.schemas.test import TestCreate, TestRead, TestReadSimple, ProgressResponse
from src.interfaces.schemas.request import RequestCreate, RequestRead

router = APIRouter(prefix="/tests")


@router.post("", response_model=TestRead)
async def create_test(data: TestCreate):
    """Создать тестовый слой (чтобы в будущем добавлять json запросы)"""

    os.makedirs(settings.STORAGE, exist_ok=True)
    test_id = unique_test_id(settings.STORAGE, data.name)
    test_dir = os.path.join(settings.STORAGE, test_id)
    os.makedirs(os.path.join(test_dir, "requests"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "responses"), exist_ok=True)

    # FS is the source of truth: name is derived from directory name.
    request_files = list_request_files(test_id)
    requests = []
    for rf in request_files:
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

    return {"id": test_id, "name": test_id, "status": get_test_status(test_id), "requests": requests}


@router.get("/{test_id}", response_model=TestRead)
async def get_test(test_id: str):
    """Получить тест со связанными запросами/ответами"""
    test_dir = os.path.join(settings.STORAGE, test_id)
    if not os.path.exists(test_dir):
        raise HTTPException(status_code=404, detail="Test not found")

    request_files = list_request_files(test_id)
    requests = []
    for rf in request_files:
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

    return {"id": test_id, "name": test_id, "status": get_test_status(test_id), "requests": requests}


@router.get("", response_model=list[TestReadSimple])
async def list_tests():
    """Список созданных тестов со статусами"""
    return [{"id": tid, "name": tid, "status": get_test_status(tid)} for tid in list_test_ids()]


@router.post("/{test_id}/requests", response_model=RequestRead)
async def create_request(
        test_id: str,
        data: RequestCreate,
):
    """
    Создать запрос внутри теста
    Пример тела запроса:
        {
          "payload": {
          "model": "qwen3.5:27b",
          "messages": [
            { "role": "system", "content": "Ты эксперт по Python. Отвечай кратко и только кодом." },
            { "role": "user", "content": "Как объединить два словаря?" }
          ],
          "stream": false,
          "options": { "temperature": 0.2, "num_ctx": 2048 }
          }
        }
    """
    storage = LocalStorageService()

    test_dir = os.path.join(settings.STORAGE, test_id)
    if not os.path.exists(test_dir):
        raise HTTPException(status_code=404, detail="Test not found")

    rid = unique_request_id()
    file_name = f"{rid}.json"
    file_path = os.path.join(test_dir, "requests", file_name)

    await storage.save_json(file_path, data.payload)

    return {"id": rid, "test_id": test_id, "file_path": file_path, "status": "pending"}


@router.delete("/{test_id}")
async def delete_test(test_id: str):
    """Удалить тест по id"""
    from src.core.config import settings
    storage = LocalStorageService()

    test_dir = os.path.join(settings.STORAGE, test_id)
    if not os.path.exists(test_dir):
        raise HTTPException(status_code=404, detail="Test not found")

    await storage.remove_tree(test_dir)

    return {"status": "deleted"}


@router.post("/{test_id}/run")
async def run_test(test_id: str):
    """Прогнать через LLM все запросы внутри теста по id(МОК)"""
    service = RunTestService(
        LocalStorageService(),
        MockLLMClient(),
    )

    asyncio.create_task(service.run_with_status(test_id))

    return {"status": "started"}

@router.get("/{test_id}/requests/{request_id}/payload")
async def get_request_payload(test_id: str, request_id: str):
    """Получить содержимое payload json для request внутри test (без передачи file_path)"""

    test_dir = os.path.join(settings.STORAGE, test_id)
    if not os.path.exists(test_dir):
        raise HTTPException(status_code=404, detail="Test not found")

    # Strictly derive path from ids to avoid arbitrary file reads.
    request_path = os.path.join(test_dir, "requests", f"{request_id}.json")
    if not os.path.exists(request_path):
        raise HTTPException(status_code=404, detail="Request payload not found")

    storage = LocalStorageService()
    data = await storage.read_json(request_path)
    return {"test_id": test_id, "request_id": request_id, "file_path": request_path, "payload": data}


@router.put("/{test_id}/requests/{request_id}/payload")
async def save_request_payload(test_id: str, request_id: str, data: RequestCreate):
    """Перезаписать payload json для request внутри test (без передачи file_path)"""

    test_dir = os.path.join(settings.STORAGE, test_id)
    if not os.path.exists(test_dir):
        raise HTTPException(status_code=404, detail="Test not found")

    request_path = os.path.join(test_dir, "requests", f"{request_id}.json")
    if not os.path.exists(request_path):
        raise HTTPException(status_code=404, detail="Request payload not found")

    storage = LocalStorageService()
    await storage.save_json(request_path, data.payload)
    return {"status": "saved", "test_id": test_id, "request_id": request_id, "file_path": request_path}


@router.delete("/{test_id}/requests/{request_id}/payload")
async def delete_request_payload(test_id: str, request_id: str):
    """Удалить request payload файл и связанные response файлы (если существуют)"""

    test_dir = os.path.join(settings.STORAGE, test_id)
    if not os.path.exists(test_dir):
        raise HTTPException(status_code=404, detail="Test not found")

    request_path = os.path.join(test_dir, "requests", f"{request_id}.json")
    if not os.path.exists(request_path):
        raise HTTPException(status_code=404, detail="Request payload not found")

    storage = LocalStorageService()
    await storage.remove_file(request_path)

    responses_dir = os.path.join(test_dir, "responses")
    ok_path = os.path.join(responses_dir, f"response_{request_id}.json")
    meta_path = os.path.join(responses_dir, f"response_{request_id}.meta.json")
    err_path = os.path.join(responses_dir, f"response_{request_id}.error.json")

    await storage.remove_file(ok_path)
    await storage.remove_file(meta_path)
    await storage.remove_file(err_path)

    return {"status": "deleted", "test_id": test_id, "request_id": request_id}


@router.get("/{test_id}/requests/{request_id}/response")
async def get_request_response(test_id: str, request_id: str):
    """Получить содержимое response json + meta/error (если есть) для request внутри test"""

    test_dir = os.path.join(settings.STORAGE, test_id)
    if not os.path.exists(test_dir):
        raise HTTPException(status_code=404, detail="Test not found")

    responses_dir = os.path.join(test_dir, "responses")
    ok_path = os.path.join(responses_dir, f"response_{request_id}.json")
    meta_path = os.path.join(responses_dir, f"response_{request_id}.meta.json")
    err_path = os.path.join(responses_dir, f"response_{request_id}.error.json")

    storage = LocalStorageService()

    ok = await storage.read_json(ok_path) if os.path.exists(ok_path) else None
    meta = await storage.read_json(meta_path) if os.path.exists(meta_path) else None
    err = await storage.read_json(err_path) if os.path.exists(err_path) else None

    if ok is None and meta is None and err is None:
        raise HTTPException(status_code=404, detail="Response not found")

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


@router.get("/{test_id}/progress", response_model=ProgressResponse)
async def get_progress_route(test_id: str):
    """Получить статус теста по id со статусами всех запросов"""
    if not os.path.exists(os.path.join(settings.STORAGE, test_id)):
        raise HTTPException(status_code=404, detail="Test not found")
    return get_progress(test_id)


@router.websocket("/ws/{test_id}")
async def ws_progress(websocket: WebSocket, test_id: str):
    await safe_ws_progress(websocket, test_id)
