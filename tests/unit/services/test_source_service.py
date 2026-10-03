import pytest

from app.models.source import SearchResult, Source
from app.providers.web.base import WebProvider
from app.services.source_service import SourceService
from app.tools.web_fetch import WebFetchTool


class FakeWebProvider(WebProvider):
    """Fake web provider for source service tests."""

    def __init__(
        self,
        source: Source,
    ) -> None:
        self.source = source
        self.last_url: str | None = None

    async def fetch(
        self,
        url: str,
    ) -> Source:
        self.last_url = url
        return self.source


@pytest.mark.asyncio
async def test_source_service_fetches_search_result():
    source = Source(
        source_id="source-1",
        title="Generative AI Report",
        url="https://example.com/report",
        domain="example.com",
        content="Full source content.",
        source_type="article",
        retrieved_at="2026-10-03T00:00:00Z",
    )

    provider = FakeWebProvider(source)

    web_fetch_tool = WebFetchTool(
        provider=provider,
    )

    service = SourceService(
        web_fetch_tool=web_fetch_tool,
    )

    search_result = SearchResult(
        title="Generative AI Report",
        url="https://example.com/report",
        snippet="Research information.",
    )

    result = await service.fetch_source(
        search_result,
    )

    assert result == source
    assert provider.last_url == "https://example.com/report"
