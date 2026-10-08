from app.config.settings import Settings
from app.dependencies import build_configured_research_service, build_research_service
from app.providers.extraction.base import ExtractionProvider
from app.providers.llm.base import LLMProvider
from app.providers.search.base import SearchProvider
from app.providers.web.base import WebProvider
from app.services.research_service import ResearchService


class FakeLLMProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        return "{}"


class FakeSearchProvider(SearchProvider):
    async def search(self, query: str, max_results: int = 10):
        return []


class FakeWebProvider(WebProvider):
    async def fetch(self, url: str):
        raise NotImplementedError


class FakeExtractionProvider(ExtractionProvider):
    async def extract(self, source, question):
        return []


def test_build_research_service():
    service = build_research_service(
        llm_provider=FakeLLMProvider(),
        search_provider=FakeSearchProvider(),
        web_provider=FakeWebProvider(),
        extraction_provider=FakeExtractionProvider(),
    )

    assert isinstance(service, ResearchService)


def test_build_configured_research_service():
    settings = Settings(
        llm_provider="openai",
        llm_model="test-model",
        openai_api_key="test-api-key",
        search_provider="tavily",
        tavily_api_key="test-api-key",
        max_search_results=5,
        max_tool_calls=10,
        max_research_iterations=2,
    )

    service = build_configured_research_service(
        settings=settings,
        web_provider=FakeWebProvider(),
        extraction_provider=FakeExtractionProvider(),
    )

    assert isinstance(service, ResearchService)
