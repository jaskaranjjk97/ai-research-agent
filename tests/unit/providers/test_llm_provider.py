import pytest

from app.providers.llm.base import LLMProvider


class FakeLLMProvider(LLMProvider):
    """A fake implementation of LLMProvider for testing purposes."""

    async def generate(self, prompt: str) -> str:
        return f"Fake response to : {prompt}"


def test_llm_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


@pytest.mark.asyncio
async def test_fake_llm_provider_can_generate():
    provider = FakeLLMProvider()

    response = await provider.generate(prompt="What is Artificial Intelligence?")

    assert response == "Fake response to : What is Artificial Intelligence?"
