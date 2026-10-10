import pytest
import tavily

from app.providers.errors import ProviderError
from app.providers.search.tavily import TavilySearchProvider


class FakeTavilyClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def search(self, query, max_results, timeout):
        self.calls.append(
            {
                "query": query,
                "max_results": max_results,
                "timeout": timeout,
            }
        )
        return self.response


@pytest.mark.asyncio
async def test_search_returns_results():
    fake_response = {
        "results": [
            {
                "title": "Python",
                "url": "https://python.org",
                "content": "Python is a programming language.",
            }
        ]
    }

    provider = TavilySearchProvider(api_key="test-key")

    fake_client = FakeTavilyClient(fake_response)
    provider.client = fake_client

    results = await provider.search(
        query="Python",
        max_results=5,
    )

    assert len(results) == 1
    assert results[0].title == "Python"
    assert str(results[0].url) == "https://python.org/"
    assert results[0].snippet == "Python is a programming language."
    assert fake_client.calls == [
        {
            "query": "Python",
            "max_results": 5,
            "timeout": 30.0,
        }
    ]


def test_empty_api_key_raises_error():
    with pytest.raises(ValueError, match="Tavily API key cannot be empty."):
        TavilySearchProvider(api_key="")


async def test_empty_query_raises_error():
    provider = TavilySearchProvider(api_key="test-key")

    with pytest.raises(ValueError, match="Search query cannot be empty."):
        await provider.search("")


@pytest.mark.asyncio
async def test_invalid_max_results_raise_error():
    provider = TavilySearchProvider(api_key="test-key")

    with pytest.raises(ValueError, match="max_results must be at least 1."):
        await provider.search("python", max_results=0)


def test_invalid_timeout_raises_error():
    with pytest.raises(
        ValueError,
        match="timeout must be greater than 0.",
    ):
        TavilySearchProvider(
            api_key="test-key",
            timeout=0,
        )


@pytest.mark.asyncio
async def test_search_translates_tavily_api_error():
    provider = TavilySearchProvider(api_key="test-key")

    class FailingTavilyClient:
        async def search(self, query, max_results, timeout):
            raise tavily.InvalidAPIKeyError("Invalid API key")

    provider.client = FailingTavilyClient()

    with pytest.raises(
        ProviderError,
        match="The web search provider request failed.",
    ) as exc_info:
        await provider.search("Python")

    assert isinstance(
        exc_info.value.__cause__,
        tavily.InvalidAPIKeyError,
    )
