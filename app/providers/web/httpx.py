from datetime import UTC, datetime

import httpx

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

        return Source(
            source_id=url,
            title=url,
            url=url,
            domain=httpx.URL(url).host or "",
            content=response.text,
            retrieved_at=datetime.now(UTC),
        )
