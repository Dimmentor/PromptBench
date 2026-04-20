from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    IS_PRODUCTION: bool = False

    STORAGE: str = "./storage"
    LOGS_DIRECTORY: str = "./logs"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.env"),
        extra="ignore",
    )


settings = Settings()