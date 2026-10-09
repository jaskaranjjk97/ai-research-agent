from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import httpx
from bs4 import BeautifulSoup

from app.models.source import Source
from app.providers.web.base import WebProvider


class HttpxWebProvider(WebProvider):
    """HTTPX implementation of the web provider."""

    def __init__(
        self,
        timeout: float = 20.0,
        user_agent: str = "ai-research-agent/0.1",
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0.")

        if not user_agent.strip():
            raise ValueError("user_agent cannot be empty.")

        self.timeout = timeout
        self.user_agent = user_agent

    async def fetch(self, url: str) -> Source:
        if not url.strip():
            raise ValueError("URL cannot be empty.")

        headers = {"User-Agent": self.user_agent}

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        page_url = str(response.url)
        parsed_url = httpx.URL(page_url)
        content_type = response.headers.get("content-type", "").lower()

        if "text/html" in content_type or "application/xhtml+xml" in content_type:
            title, content, published_at = self._parse_html(response.text)
        else:
            title = page_url
            content = response.text.strip()
            published_at = None

        if not content:
            raise ValueError(f"No readable content found at {page_url}.")

        return Source(
            source_id=page_url,
            title=title or page_url,
            url=page_url,
            domain=parsed_url.host or "",
            content=content,
            published_at=published_at,
            retrieved_at=datetime.now(UTC),
        )

    @staticmethod
    def _parse_html(
        html: str,
    ) -> tuple[str, str, datetime | None]:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "noscript", "template", "svg"]):
            element.decompose()

        title = ""
        if soup.title:
            title = soup.title.get_text(" ", strip=True)

        published_at = HttpxWebProvider._extract_published_at(soup)

        main = soup.find("main") or soup.find("article") or soup.body or soup
        content = main.get_text(" ", strip=True)

        return title, content, published_at

    @staticmethod
    def _extract_published_at(soup: BeautifulSoup) -> datetime | None:
        meta_names = (
            "article:published_time",
            "datePublished",
            "pubdate",
            "publishdate",
            "date",
        )

        for name in meta_names:
            tag = soup.find("meta", attrs={"property": name})
            if tag is None:
                tag = soup.find("meta", attrs={"name": name})

            if tag is None:
                continue

            value = tag.get("content")
            if not isinstance(value, str) or not value.strip():
                continue

            try:
                return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
            except ValueError:
                try:
                    return parsedate_to_datetime(value.strip())
                except (TypeError, ValueError, OverflowError):
                    continue

        return None
