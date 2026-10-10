import openai
from openai import AsyncOpenAI

from app.providers.errors import ProviderError
from app.providers.llm.base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    """OpenAI implementation of the LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenAI API key cannot be empty.")

        if not model.strip():
            raise ValueError("OpenAI model cannot be empty.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0.")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.model = model

    async def generate(self, prompt: str) -> str:
        """Generate text using the OpenAI Responses API."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = await self.client.responses.create(
                model=self.model,
                input=prompt,
            )
        except openai.APIError as exc:
            raise ProviderError("The language model provider request failed.") from exc

        return response.output_text
