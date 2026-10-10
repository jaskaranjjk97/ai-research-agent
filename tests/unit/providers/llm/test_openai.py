from unittest.mock import patch

import openai
import pytest

from app.providers.errors import ProviderError
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


def test_constructor_rejects_invalid_timeout():
    with pytest.raises(
        ValueError,
        match="timeout must be greater than 0.",
    ):
        OpenAILLMProvider(
            api_key="test-key",
            model="test-model",
            timeout=0,
        )


def test_constructor_rejects_negative_retries():
    with pytest.raises(
        ValueError,
        match="max_retries cannot be negative.",
    ):
        OpenAILLMProvider(
            api_key="test-key",
            model="test-model",
            max_retries=-1,
        )


def test_constructor_passes_timeout_and_retries_to_client():
    with patch("app.providers.llm.openai.AsyncOpenAI") as mock_client:
        OpenAILLMProvider(
            api_key="test-key",
            model="test-model",
            timeout=25.0,
            max_retries=4,
        )

    mock_client.assert_called_once_with(
        api_key="test-key",
        timeout=25.0,
        max_retries=4,
    )


async def test_generate_translates_openai_api_error():
    provider = OpenAILLMProvider(
        api_key="test-key",
        model="test-model",
    )

    class FailingResponses:
        async def create(self, model, input):
            raise openai.APIConnectionError(request=None)

    class FailingClient:
        responses = FailingResponses()

    provider.client = FailingClient()

    with pytest.raises(
        ProviderError,
        match="The language model provider request failed.",
    ) as exc_info:
        await provider.generate("Say hello.")

    assert isinstance(exc_info.value.__cause__, openai.APIConnectionError)


async def test_generate_does_not_translate_empty_prompt():
    provider = OpenAILLMProvider(
        api_key="test-key",
        model="test-model",
    )

    with pytest.raises(ValueError, match="Prompt cannot be empty."):
        await provider.generate("")
