from src.infrastructure.storage.local import LocalStorageService
from src.infrastructure.llm.mock_client import MockLLMClient


def get_storage():
    return LocalStorageService()


def get_llm_client():
    return MockLLMClient()