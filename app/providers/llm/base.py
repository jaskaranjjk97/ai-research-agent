from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for large language model."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response from language model."""

        raise NotImplementedError
