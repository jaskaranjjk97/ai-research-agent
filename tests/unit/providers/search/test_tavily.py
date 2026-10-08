import pytest

from app.providers.search.tavily import TavilySearchProvider


class FakeTavilyClient:
    def __init__(self, response):
        self.response = response

    def search(self, query, max_results):
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

    provider.client = FakeTavilyClient(fake_response)

    results = await provider.search(
        query="Python",
        max_results=5,
    )

    assert len(results) == 1
    assert results[0].title == "Python"
    assert str(results[0].url) == "https://python.org/"
    assert results[0].snippet == "Python is a programming language."


def test_empty_api_key_raises_error():
    with pytest.raises(ValueError, match="Tavily API key cannot be empty."):
        TavilySearchProvider(api_key="")


async def test_empty_query_raises_error():
    provider = TavilySearchProvider(api_key="test-key")

    with pytest.raises(ValueError, match="Search query cannot be empty."):
        await provider.search("")
