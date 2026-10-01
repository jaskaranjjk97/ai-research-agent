from abc import ABC, abstractmethod

from app.models.source import SearchResult


class SearchProvider(ABC):
    """Abstract interface for web search providers."""

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search the web and return normalized search results."""
        raise NotImplementedError
