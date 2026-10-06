from app.dependencies import build_research_service
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
