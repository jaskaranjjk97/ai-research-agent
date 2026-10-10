from unittest.mock import patch

import pytest

from app.config.settings import Settings
from app.providers.factory import create_llm_provider, create_search_provider
from app.providers.llm.openai import OpenAILLMProvider
from app.providers.search.tavily import TavilySearchProvider


def test_create_openai_provider():
    settings = Settings(
        llm_provider="openai",
        llm_model="test-model",
        openai_api_key="test-api-key",
        llm_timeout_seconds=25.0,
        llm_max_retries=4,
    )

    with patch("app.providers.llm.openai.AsyncOpenAI") as mock_client:
        provider = create_llm_provider(settings)

    assert isinstance(provider, OpenAILLMProvider)
    assert provider.model == "test-model"
    mock_client.assert_called_once_with(
        api_key="test-api-key",
        timeout=25.0,
        max_retries=4,
    )


def test_unsupported_llm_provider_raises_error():
    settings = Settings(
        llm_provider="unsupported",
        llm_model="test-model",
        openai_api_key="test-api-key",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported LLM provider: unsupported",
    ):
        create_llm_provider(settings)


def test_create_tavily_search_provider():
    settings = Settings(
        search_provider="tavily",
        tavily_api_key="test-api-key",
        search_timeout_seconds=18.0,
    )

    with patch("app.providers.search.tavily.AsyncTavilyClient") as mock_client:
        provider = create_search_provider(settings)

    assert isinstance(provider, TavilySearchProvider)
    assert provider.timeout == 18.0
    mock_client.assert_called_once_with(api_key="test-api-key")


def test_unsupported_search_provider_raises_error():
    settings = Settings(
        search_provider="unsupported",
        tavily_api_key="test-api-key",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported search provider: unsupported",
    ):
        create_search_provider(settings)


def test_empty_llm_model_raises_clear_error():
    settings = Settings(
        llm_provider="openai",
        llm_model="",
        openai_api_key="test-api-key",
    )

    with pytest.raises(ValueError, match="OpenAI model cannot be empty"):
        create_llm_provider(settings)


def test_empty_openai_api_key_raises_clear_error():
    settings = Settings(
        llm_provider="openai",
        llm_model="test-model",
        openai_api_key="",
    )

    with pytest.raises(ValueError, match="OpenAI API key cannot be empty"):
        create_llm_provider(settings)


def test_empty_tavily_api_key_raises_clear_error():
    settings = Settings(
        search_provider="tavily",
        tavily_api_key="",
    )

    with pytest.raises(ValueError, match="Tavily API key cannot be empty"):
        create_search_provider(settings)


def test_create_openai_provider_accepts_uppercase_provider_name():
    settings = Settings(
        llm_provider="OPENAI",
        llm_model="test-model",
        openai_api_key="test-api-key",
    )

    with patch("app.providers.llm.openai.AsyncOpenAI"):
        provider = create_llm_provider(settings)

    assert isinstance(provider, OpenAILLMProvider)


def test_create_tavily_provider_accepts_uppercase_provider_name():
    settings = Settings(
        search_provider="TAVILY",
        tavily_api_key="test-api-key",
    )

    with patch("app.providers.search.tavily.AsyncTavilyClient"):
        provider = create_search_provider(settings)

    assert isinstance(provider, TavilySearchProvider)
