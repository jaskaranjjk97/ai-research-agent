from abc import ABC, abstractmethod

from app.models.source import Source


class WebProvider(ABC):
    """Abstract interface for web services."""

    @abstractmethod
    async def fetch(self, url: str) -> Source:
        """This function fetched the web pages and normalize to Source."""
        raise NotImplementedError
