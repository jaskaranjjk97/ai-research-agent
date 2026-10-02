import pytest
from pydantic import HttpUrl

from app.models.source import SearchResult
from app.providers.search.base import SearchProvider
from app.tools.execution import (
    ToolExecutionController,
    ToolExecutionLimitError,
)
from app.tools.search import SearchTool


class FakeSearchProvider(SearchProvider):
    """Fake search provider for SearchTool tests."""

    def __init__(self) -> None:
        self.last_query: str | None = None
        self.last_max_results: int | None = None

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        self.last_query = query
        self.last_max_results = max_results

        return [
            SearchResult(
                title="AI Research",
                url=HttpUrl("https://example.com/ai"),
                snippet="Research information.",
                source_name="Example",
            )
        ]


@pytest.mark.asyncio
async def test_search_tool_calls_provider():
    provider = FakeSearchProvider()

    tool = SearchTool(
        provider=provider,
        max_results=5,
    )

    results = await tool.search("artificial intelligence research")

    assert len(results) == 1
    assert results[0].title == "AI Research"
    assert provider.last_query == "artificial intelligence research"
    assert provider.last_max_results == 5


@pytest.mark.asyncio
async def test_search_tool_rejects_empty_query():
    provider = FakeSearchProvider()

    tool = SearchTool(provider=provider)

    with pytest.raises(ValueError, match="Search query cannot be empty"):
        await tool.search("")


@pytest.mark.asyncio
async def test_search_tool_rejects_whitespace_query():
    provider = FakeSearchProvider()

    tool = SearchTool(provider=provider)

    with pytest.raises(ValueError, match="Search query cannot be empty"):
        await tool.search("   ")


@pytest.mark.asyncio
async def test_search_tool_records_execution():
    provider = FakeSearchProvider()
    execution_controller = ToolExecutionController(max_tool_calls=1)

    tool = SearchTool(provider=provider, tool_execution_controller=execution_controller)

    await tool.search("test query")

    assert execution_controller.tool_calls == 1


@pytest.mark.asyncio
async def test_search_tool_respects_execution_limit():
    provider = FakeSearchProvider()
    execution_controller = ToolExecutionController(max_tool_calls=1)

    tool = SearchTool(provider=provider, tool_execution_controller=execution_controller)

    await tool.search("test query")

    with pytest.raises(ToolExecutionLimitError):
        await tool.search("another query")

    assert execution_controller.tool_calls == 1
