import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_default_settings():
    settings = Settings()

    assert settings.app_name == "ai-research-agent"
    assert settings.max_research_iterations == 3
    assert settings.llm_provider == "openai"
    assert settings.max_search_results == 10
    assert settings.api_port == 8000
    assert settings.max_sources == 30
    assert settings.max_tool_calls == 20


def test_invalid_log_level_is_rejected():
    with pytest.raises(ValidationError):
        Settings(log_level="INVALID")
