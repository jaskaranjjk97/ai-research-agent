import pytest
from pydantic import HttpUrl

from app.models.source import SearchResult
from app.providers.search.base import SearchProvider


class FakeSearchProvider(SearchProvider):
    """Fake search implementation used for testing."""

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                title=f"Result for {query}",
                url=HttpUrl("https://example.com/research"),
                snippet="Example search result.",
                source_name="Example",
            )
        ][:max_results]


def test_search_provider_is_abstract():
    with pytest.raises(TypeError):
        SearchProvider()


@pytest.mark.asyncio
async def test_concrete_search_provider_returns_search_results():
    provider = FakeSearchProvider()

    results = await provider.search(
        query="electric vehicle adoption",
        max_results=5,
    )

    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert results[0].title == "Result for electric vehicle adoption"


@pytest.mark.asyncio
async def test_search_provider_respects_max_results():
    provider = FakeSearchProvider()

    results = await provider.search(
        query="AI research",
        max_results=0,
    )

    assert results == []
