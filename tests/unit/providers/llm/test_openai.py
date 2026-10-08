import pytest

from app.providers.llm.openai import OpenAILLMProvider


class FakeOpenAIClient:
    def __init__(self, response_text: str):
        self.response_text = response_text

    class Responses:
        def __init__(self, response_text: str):
            self.response_text = response_text

        async def create(self, model, input):
            return type(
                "Response",
                (),
                {"output_text": self.response_text},
            )()

    @property
    def responses(self):
        return self.Responses(self.response_text)


async def test_generate_returns_response():
    provider = OpenAILLMProvider(
        api_key="test-key",
        model="test-model",
    )

    provider.client = FakeOpenAIClient(
        response_text="Hello from the LLM",
    )

    result = await provider.generate("Say hello.")

    assert result == "Hello from the LLM"


def test_empty_api_key_raises_error():
    with pytest.raises(ValueError, match="OpenAI API key cannot be empty."):
        OpenAILLMProvider(
            api_key="",
            model="test-model",
        )


async def test_empty_prompt_raises_error():
    provider = OpenAILLMProvider(
        api_key="test-key",
        model="test-model",
    )

    with pytest.raises(ValueError, match="Prompt cannot be empty."):
        await provider.generate("")
