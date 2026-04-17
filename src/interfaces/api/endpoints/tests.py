import os
import asyncio
from fastapi import APIRouter, Depends, WebSocket, HTTPException

from src.application.services.websocket import safe_ws_progress
from src.core.database import get_session
from src.infrastructure.repositories.test_repository import TestRepository
from src.infrastructure.repositories.request_repository import RequestRepository
from src.infrastructure.storage.local import LocalStorageService
from src.infrastructure.llm.mock_client import MockLLMClient
from src.application.services.test_service import TestService
from src.application.services.run_test_service import RunTestService
from src.interfaces.schemas.test import TestCreate, TestRead, TestReadSimple, ProgressResponse
from src.interfaces.schemas.request import RequestCreate, RequestRead

router = APIRouter(prefix="/tests")


@router.post("", response_model=TestRead)
async def create_test(data: TestCreate, session=Depends(get_session)):
    """Создать тестовый слой (чтобы в будущем добавлять json запросы)"""
    repo = TestRepository(session)
    service = TestService(repo)
    return await service.create_test(data.name)


@router.get("/{test_id}", response_model=TestRead)
async def get_test(test_id: int, session=Depends(get_session)):
    """Получить тест со связанными запросами/ответами"""
    repo = TestRepository(session)
    test = await repo.get_with_requests(test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


@router.get("", response_model=list[TestReadSimple])
async def list_tests(session=Depends(get_session)):
    """Список созданных тестов со статусами"""
    repo = TestRepository(session)
    return await repo.list()


@router.post("/{test_id}/requests", response_model=RequestRead)
async def create_request(
        test_id: int,
        data: RequestCreate,
        session=Depends(get_session),
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
    test_repo = TestRepository(session)
    request_repo = RequestRepository(session)
    storage = LocalStorageService()

    test = await test_repo.get(test_id)

    # Create request first to get database ID
    request = await request_repo.create(test_id, "")

    # Use the database ID for file naming
    file_name = f"request_{request.id}.json"
    file_path = os.path.join(test.storage_path, "requests", file_name)

    await storage.save_json(file_path, data.payload)

    # Update the request with the correct file path
    request.file_path = file_path
    await session.commit()
    await session.refresh(request)

    return request


@router.delete("/{test_id}")
async def delete_test(test_id: int, session=Depends(get_session)):
    """Удалить тест по id"""
    repo = TestRepository(session)
    test = await repo.get(test_id)

    await session.delete(test)
    await session.commit()

    return {"status": "deleted"}


@router.post("/{test_id}/run")
async def run_test(test_id: int, session=Depends(get_session)):
    """Прогнать через LLM все запросы внутри теста по id(МОК)"""
    test_repo = TestRepository(session)
    request_repo = RequestRepository(session)

    service = RunTestService(
        test_repo,
        request_repo,
        LocalStorageService(),
        MockLLMClient(),
    )

    asyncio.create_task(service.run_with_status(test_id))

    return {"status": "started"}


@router.get("/{test_id}/progress", response_model=ProgressResponse)
async def get_progress(test_id: int, session=Depends(get_session)):
    """Получить статус теста по id со статусами всех запросов"""
    repo = TestRepository(session)
    return await repo.get_progress(test_id)


@router.websocket("/ws/{test_id}")
async def ws_progress(websocket: WebSocket, test_id: int):
    await safe_ws_progress(websocket, test_id)
