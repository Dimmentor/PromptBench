from src.application.services.gateway_app_service import GatewayApplicationService
from src.application.services.test_app_service import TestApplicationService
from src.infrastructure.llm.orchestrator_client import OrchestratorLLMClient
from src.infrastructure.storage.local import LocalStorageService


def get_storage():
    return LocalStorageService()


def get_llm_client():
    return OrchestratorLLMClient()


def get_test_application_service() -> TestApplicationService:
    return TestApplicationService(get_storage(), get_llm_client)


def get_gateway_application_service() -> GatewayApplicationService:
    return GatewayApplicationService(get_llm_client())