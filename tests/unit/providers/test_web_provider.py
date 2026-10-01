from datetime import UTC, datetime

import pytest
from pydantic import HttpUrl

from app.models.source import Source
from app.providers.web.base import WebProvider


class FakeWebProvider(WebProvider):
    """Fake web implementation used for testing."""

    async def fetch(
        self,
        url: str,
    ) -> Source:
        return Source(
            source_id="source-001",
            title="Example Research Page",
            url=HttpUrl(url),
            domain="example.com",
            content="This is example web page content.",
            source_type="webpage",
            retrieved_at=datetime.now(UTC),
        )


def test_web_provider_is_abstract():
    with pytest.raises(TypeError):
        WebProvider()


@pytest.mark.asyncio
async def test_concrete_web_provider_returns_source():
    provider = FakeWebProvider()

    source = await provider.fetch("https://example.com/research")

    assert isinstance(source, Source)
    assert source.source_id == "source-001"
    assert source.domain == "example.com"
    assert source.content == "This is example web page content."


@pytest.mark.asyncio
async def test_web_provider_preserves_requested_url():
    provider = FakeWebProvider()

    source = await provider.fetch("https://example.com/article")

    assert str(source.url) == "https://example.com/article"
