from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    IS_PRODUCTION: bool = False

    STORAGE: str = "./storage"
    LOGS_DIRECTORY: str = "./logs"

    # Workshop Orchestrator (OpenAI-compatible)
    ORCHESTRATOR_BASE_URL: str = "http://localhost:8001"
    ORCHESTRATOR_TIMEOUT_SECONDS: float = 600.0

    LLM_MAX_CONCURRENT_REQUESTS: int = 1

    model_config = SettingsConfigDict(
        env_file=[
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.env"),
        ],
        extra="ignore",
    )


settings = Settings()

print(settings.STORAGE)