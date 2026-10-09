import pytest

from app.models.research import ResearchQuestion
from app.models.source import Source
from app.providers.extraction.llm import LLMExtractionProvider
from app.providers.llm.base import LLMProvider


class FakeLLMProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        return (
            '[{"evidence_id": "ev-1", '
            '"content": "Python supports asynchronous programming.", '
            '"location": "Concurrency"}]'
        )


@pytest.mark.asyncio
async def test_extract_returns_evidence():
    provider = LLMExtractionProvider(FakeLLMProvider())

    source = Source(
        source_id="src-1",
        title="Python documentation",
        url="https://python.org",
        domain="python.org",
        content="Python supports asynchronous programming.",
        retrieved_at="2026-10-09T10:00:00Z",
    )

    question = ResearchQuestion(
        id="q-1",
        question="How does Python support asynchronous programming?",
    )

    evidences = await provider.extract(source, question)

    assert len(evidences) == 1
    assert evidences[0].evidence_id == "ev-1"
    assert evidences[0].source_id == "src-1"
    assert evidences[0].question_id == "q-1"
    assert evidences[0].content == ("Python supports asynchronous programming.")


@pytest.mark.asyncio
async def test_extract_returns_empty_list_when_no_evidence():
    class EmptyFakeLLMProvider(LLMProvider):
        async def generate(self, prompt: str) -> str:
            return "[]"

    provider = LLMExtractionProvider(EmptyFakeLLMProvider())

    source = Source(
        source_id="src-1",
        title="Python documentation",
        url="https://python.org",
        domain="python.org",
        content="A page about something unrelated.",
        retrieved_at="2026-10-09T10:00:00Z",
    )

    question = ResearchQuestion(
        id="q-1",
        question="How does Python support asynchronous programming?",
    )

    evidences = await provider.extract(source, question)

    assert evidences == []
