from src.infrastructure.storage.local import LocalStorageService
from src.infrastructure.llm.orchestrator_client import OrchestratorLLMClient


def get_storage():
    return LocalStorageService()


def get_llm_client():
    return OrchestratorLLMClient()