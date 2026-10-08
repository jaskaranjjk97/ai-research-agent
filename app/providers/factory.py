from app.config.settings import Settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.openai import OpenAILLMProvider
from app.providers.search.base import SearchProvider
from app.providers.search.tavily import TavilySearchProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Create the configured LLM provider."""

    if settings.llm_provider == "openai":
        return OpenAILLMProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def create_search_provider(settings: Settings) -> SearchProvider:
    """Create the configured search provider."""

    if settings.search_provider == "tavily":
        return TavilySearchProvider(
            api_key=settings.tavily_api_key,
        )

    raise ValueError(f"Unsupported search provider: {settings.search_provider}")
