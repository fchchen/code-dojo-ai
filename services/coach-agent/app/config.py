from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COACH_", extra="ignore")

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"
    ml_analyzer_url: str = "http://ml-analyzer:8001"
    sqlite_path: str = "./data/coach_agent.db"
    max_agent_iterations: int = 10
    request_timeout_seconds: float = 20.0
    llm_timeout_seconds: float = 20.0
    cors_origins: list[str] = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
