from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/researchiq"
    SEC_USER_AGENT: str = "ResearchIQ research@example.com"
    MAX_NEWS_HEADLINES: int = 10
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    REQUEST_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
