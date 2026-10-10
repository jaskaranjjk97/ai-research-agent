from app.config.settings import Settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.openai import OpenAILLMProvider
from app.providers.search.base import SearchProvider
from app.providers.search.tavily import TavilySearchProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Create the configured LLM provider."""

    if settings.llm_provider.strip().lower() == "openai":
        return OpenAILLMProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def create_search_provider(settings: Settings) -> SearchProvider:
    """Create the configured search provider."""

    if settings.search_provider.strip().lower() == "tavily":
        return TavilySearchProvider(
            api_key=settings.tavily_api_key,
            timeout=settings.search_timeout_seconds,
        )

    raise ValueError(f"Unsupported search provider: {settings.search_provider}")
