from openai import AsyncOpenAI

from app.providers.llm.base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    """OpenAI implementation of the LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenAI API key cannot be empty.")

        if not model.strip():
            raise ValueError("OpenAI model cannot be empty.")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str) -> str:
        """Generate text using the OpenAI Responses API."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text
