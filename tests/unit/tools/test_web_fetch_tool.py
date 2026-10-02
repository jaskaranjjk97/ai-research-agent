from datetime import UTC, datetime

import pytest
from pydantic import HttpUrl

from app.models.source import Source
from app.providers.web.base import WebProvider
from app.tools.execution import ToolExecutionController, ToolExecutionLimitError
from app.tools.web_fetch import WebFetchTool


class FakeWebProvider(WebProvider):
    """Fake web provider for WebFetchTool tests."""

    def __init__(self) -> None:
        self.last_url: str | None = None

    async def fetch(
        self,
        url: str,
    ) -> Source:
        self.last_url = url

        return Source(
            source_id="source-001",
            title="Example Research",
            url=HttpUrl(url),
            domain="example.com",
            content="Example research content.",
            source_type="webpage",
            retrieved_at=datetime.now(UTC),
        )


@pytest.mark.asyncio
async def test_web_fetch_tool_calls_provider():
    provider = FakeWebProvider()

    tool = WebFetchTool(
        provider=provider,
    )

    source = await tool.fetch("https://example.com/research")

    assert isinstance(source, Source)
    assert source.source_id == "source-001"
    assert source.title == "Example Research"
    assert provider.last_url == "https://example.com/research"


@pytest.mark.asyncio
async def test_web_fetch_tool_rejects_empty_url():
    provider = FakeWebProvider()

    tool = WebFetchTool(
        provider=provider,
    )

    with pytest.raises(ValueError, match="URL cannot be empty"):
        await tool.fetch("")


@pytest.mark.asyncio
async def test_web_fetch_tool_rejects_whitespace_url():
    provider = FakeWebProvider()

    tool = WebFetchTool(
        provider=provider,
    )

    with pytest.raises(ValueError, match="URL cannot be empty"):
        await tool.fetch("   ")


@pytest.mark.asyncio
async def test_web_fetch_tool_records_tool_execution():
    provider = FakeWebProvider()

    controller = ToolExecutionController(
        max_tool_calls=2,
    )

    tool = WebFetchTool(
        provider=provider,
        tool_execution_controller=controller,
    )

    await tool.fetch("https://example.com/resaerch")

    assert controller.tool_calls == 1


@pytest.mark.asyncio
async def test_web_fetch_tool_respects_execution_limit():
    provider = FakeWebProvider()

    controller = ToolExecutionController(
        max_tool_calls=1,
    )

    tool = WebFetchTool(
        provider=provider,
        tool_execution_controller=controller,
    )

    await tool.fetch("https://example.com/research")

    with pytest.raises(ToolExecutionLimitError):
        await tool.fetch("https://example.org")

    assert controller.tool_calls == 1
