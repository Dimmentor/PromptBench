from fastapi import APIRouter, Depends, WebSocket

from src.application.services.test_app_service import TestApplicationService
from src.application.services.websocket import safe_ws_progress
from src.infrastructure.di import get_test_application_service
from src.interfaces.schemas.test import TestCreate, TestRead, TestReadSimple, ProgressResponse
from src.interfaces.schemas.request import RequestCreate, RequestRead

router = APIRouter(prefix="/tests")


@router.post("", response_model=TestRead)
async def create_test(
    data: TestCreate,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Создать тестовый слой (чтобы в будущем добавлять json запросы)"""
    return svc.create_test(data.name)


@router.get("/{test_id}", response_model=TestRead)
async def get_test(
    test_id: str,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Получить тест со связанными запросами/ответами"""
    return svc.get_test(test_id)


@router.get("", response_model=list[TestReadSimple])
async def list_tests(
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Список созданных тестов со статусами"""
    return svc.list_tests()


@router.post("/{test_id}/requests", response_model=RequestRead)
async def create_request(
    test_id: str,
    data: RequestCreate,
    svc: TestApplicationService = Depends(get_test_application_service),
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
    return await svc.create_request(test_id, data.payload, data.name)


@router.delete("/{test_id}")
async def delete_test(
    test_id: str,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Удалить тест по id"""
    return await svc.delete_test(test_id)


@router.post("/{test_id}/run")
async def run_test(
    test_id: str,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Прогнать через LLM все запросы внутри теста по id(МОК)"""
    return await svc.schedule_test_run(test_id)


@router.get("/{test_id}/requests/{request_id}/payload")
async def get_request_payload(
    test_id: str,
    request_id: str,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Получить содержимое payload json для request внутри test (без передачи file_path)"""
    return await svc.get_request_payload(test_id, request_id)


@router.put("/{test_id}/requests/{request_id}/payload")
async def save_request_payload(
    test_id: str,
    request_id: str,
    data: RequestCreate,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Перезаписать payload json для request внутри test (без передачи file_path)"""
    return await svc.save_request_payload(test_id, request_id, data.payload)


@router.delete("/{test_id}/requests/{request_id}/payload")
async def delete_request_payload(
    test_id: str,
    request_id: str,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Удалить request payload файл и связанные response файлы (если существуют)"""
    return await svc.delete_request_payload(test_id, request_id)


@router.get("/{test_id}/requests/{request_id}/response")
async def get_request_response(
    test_id: str,
    request_id: str,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Получить содержимое response json + meta/error (если есть) для request внутри test"""
    return await svc.get_request_response(test_id, request_id)


@router.get("/{test_id}/progress", response_model=ProgressResponse)
async def get_progress_route(
    test_id: str,
    svc: TestApplicationService = Depends(get_test_application_service),
):
    """Получить статус теста по id со статусами всех запросов"""
    return svc.get_progress(test_id)


@router.websocket("/ws/{test_id}")
async def ws_progress(websocket: WebSocket, test_id: str):
    await safe_ws_progress(websocket, test_id)
