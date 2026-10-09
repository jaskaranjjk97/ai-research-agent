import httpx
import pytest

from app.providers.web.httpx import HttpxWebProvider


class FakeAsyncClient:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None

    async def get(self, url: str, headers: dict[str, str]):
        return self.response


@pytest.mark.asyncio
async def test_fetch_returns_source(monkeypatch):
    response = httpx.Response(
        status_code=200,
        text="Python is a programming language.",
        request=httpx.Request("GET", "https://python.org"),
    )

    monkeypatch.setattr(
        "app.providers.web.httpx.httpx.AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    provider = HttpxWebProvider()
    source = await provider.fetch("https://python.org")

    assert source.title == "https://python.org"
    assert str(source.url) == "https://python.org/"
    assert source.domain == "python.org"
    assert source.content == "Python is a programming language."


@pytest.mark.asyncio
async def test_empty_url_raises_error():
    provider = HttpxWebProvider()

    with pytest.raises(ValueError, match="URL cannot be empty."):
        await provider.fetch("")
