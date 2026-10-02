from abc import ABC, abstractmethod

from app.models.evidence import Evidence
from app.models.research import ResearchQuestion
from app.models.source import Source


class ExtractionProvider(ABC):
    """Abstract interface for extraction providers."""

    @abstractmethod
    async def extract(
        self, source: Source, question: ResearchQuestion
    ) -> list[Evidence]:
        """Extracts evidence from a source based on a research question."""
        raise NotImplementedError
