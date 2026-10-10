import httpx
import tavily
from tavily import AsyncTavilyClient

from app.models.source import SearchResult
from app.providers.errors import ProviderError
from app.providers.search.base import SearchProvider


class TavilySearchProvider(SearchProvider):
    """Asynchronous Tavily implementation of the search provider."""

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("Tavily API key cannot be empty.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0.")

        self.client = AsyncTavilyClient(api_key=api_key)
        self.timeout = timeout

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search Tavily asynchronously and normalize the results."""

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if max_results < 1:
            raise ValueError("max_results must be at least 1.")

        try:
            response = await self.client.search(
                query=query,
                max_results=max_results,
                timeout=self.timeout,
            )
        except (
            tavily.BadRequestError,
            tavily.InvalidAPIKeyError,
            tavily.KeylessUnsupportedEndpointError,
            tavily.MissingAPIKeyError,
            tavily.UsageLimitExceededError,
            httpx.HTTPError,
        ) as exc:
            raise ProviderError("The web search provider request failed.") from exc

        results: list[SearchResult] = []

        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item["url"],
                    snippet=item.get("content", ""),
                    source_name=item.get("url"),
                )
            )

        return results
