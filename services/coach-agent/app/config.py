from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
