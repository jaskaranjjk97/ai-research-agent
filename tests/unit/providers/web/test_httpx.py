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


@pytest.mark.asyncio
async def test_fetch_extracts_title_and_readable_html(monkeypatch):
    response = httpx.Response(
        status_code=200,
        headers={"content-type": "text/html; charset=utf-8"},
        text="""
        <html>
            <head>
                <title>Python Async Guide</title>
                <script>ignore_this_script()</script>
                <style>.hidden { display: none; }</style>
            </head>
            <body>
                <nav>Navigation links</nav>
                <main>
                    <h1>Asynchronous Python</h1>
                    <p>Python supports asynchronous programming.</p>
                </main>
                <footer>Footer links</footer>
            </body>
        </html>
        """,
        request=httpx.Request("GET", "https://python.org/async"),
    )

    monkeypatch.setattr(
        "app.providers.web.httpx.httpx.AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    provider = HttpxWebProvider()
    source = await provider.fetch("https://python.org/async")

    assert source.title == "Python Async Guide"
    assert "Asynchronous Python" in source.content
    assert "Python supports asynchronous programming." in source.content
    assert "ignore_this_script" not in source.content
    assert "display: none" not in source.content
    assert "Navigation links" not in source.content
    assert "Footer links" not in source.content


@pytest.mark.asyncio
async def test_fetch_uses_url_when_html_has_no_title(monkeypatch):
    response = httpx.Response(
        status_code=200,
        headers={"content-type": "text/html"},
        text="<html><body><main>Useful page content</main></body></html>",
        request=httpx.Request("GET", "https://example.com/page"),
    )

    monkeypatch.setattr(
        "app.providers.web.httpx.httpx.AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    provider = HttpxWebProvider()
    source = await provider.fetch("https://example.com/page")

    assert source.title == "https://example.com/page"
    assert source.content == "Useful page content"


@pytest.mark.asyncio
async def test_fetch_raises_error_when_html_has_no_content(monkeypatch):
    response = httpx.Response(
        status_code=200,
        headers={"content-type": "text/html"},
        text="<html><head><title>Empty page</title></head><body></body></html>",
        request=httpx.Request("GET", "https://example.com/empty"),
    )

    monkeypatch.setattr(
        "app.providers.web.httpx.httpx.AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    provider = HttpxWebProvider()

    with pytest.raises(ValueError, match="No readable content found"):
        await provider.fetch("https://example.com/empty")


@pytest.mark.asyncio
async def test_fetch_raises_for_http_error(monkeypatch):
    response = httpx.Response(
        status_code=404,
        request=httpx.Request("GET", "https://example.com/missing"),
    )

    monkeypatch.setattr(
        "app.providers.web.httpx.httpx.AsyncClient",
        lambda **kwargs: FakeAsyncClient(response),
    )

    provider = HttpxWebProvider()

    with pytest.raises(httpx.HTTPStatusError):
        await provider.fetch("https://example.com/missing")
