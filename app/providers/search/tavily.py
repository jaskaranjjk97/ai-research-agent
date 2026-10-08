from tavily import TavilyClient

from app.models.source import SearchResult
from app.providers.search.base import SearchProvider


class TavilySearchProvider(SearchProvider):
    """Tavily implementation of the search provider."""

    def __init__(self, api_key: str) -> None:
        if not api_key.strip():
            raise ValueError("Tavily API key cannot be empty.")

        self.client = TavilyClient(api_key=api_key)

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search Tavily and convert results to domain models."""

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if max_results < 1:
            raise ValueError("max_results must be at least 1.")

        response = self.client.search(
            query=query,
            max_results=max_results,
        )

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
