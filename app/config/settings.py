from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings configured from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ai-research-agent"
    app_env: str = "development"
    log_level: str = Field(
        default="INFO",
        pattern="^(?i:DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )

    llm_provider: str = "openai"
    llm_model: str = ""
    openai_api_key: str = ""
    llm_timeout_seconds: float = Field(default=60.0, gt=0)
    llm_max_retries: int = Field(default=2, ge=0, le=10)

    search_provider: str = ""
    search_api_key: str = ""
    tavily_api_key: str = ""
    search_timeout_seconds: float = Field(default=30.0, gt=0)
    research_request_timeout_seconds: float = Field(default=180.0, gt=0)

    max_research_iterations: int = Field(default=3, ge=1)
    max_tool_calls: int = Field(default=20, ge=1)
    max_sources: int = Field(default=30, ge=1)
    max_search_results: int = Field(default=10, ge=1)

    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)


@lru_cache
def get_settings() -> Settings:
    """Get the cached application settings instance."""
    return Settings()
