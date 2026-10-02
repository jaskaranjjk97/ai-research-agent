from datetime import UTC, datetime

import pytest

from app.models.evidence import Evidence
from app.models.research import ResearchQuestion
from app.models.source import Source
from app.providers.extraction.base import ExtractionProvider


class FakeExtractionProvider(ExtractionProvider):
    """ "Fake extraction provider for testing."""

    async def extract(
        self, source: Source, question: ResearchQuestion
    ) -> list[Evidence]:
        return [
            Evidence(
                evidence_id="evidence-001",
                source_id=source.source_id,
                question_id=question.id,
                content="This is a piece of evidence.",
                location="Page 1, Paragraph 2",
            )
        ]


async def test_extraction_provider_is_abstract():
    with pytest.raises(TypeError):
        ExtractionProvider()


@pytest.mark.asyncio
async def test_fake_extraction_provider_extracts_evidence():
    provider = FakeExtractionProvider()

    source = Source(
        source_id="source-001",
        title="Example Research",
        url="https://example.com/research",
        domain="example.com",
        content="Example research content.",
        source_type="webpage",
        retrieved_at=datetime.now(UTC),
    )

    question = ResearchQuestion(
        id="question-001",
        question="What are the key findings of this research?",
    )

    evidence_list = await provider.extract(source, question)

    assert len(evidence_list) == 1
    assert evidence_list[0].evidence_id == "evidence-001"
    assert evidence_list[0].source_id == "source-001"
    assert evidence_list[0].question_id == "question-001"
    assert evidence_list[0].content == "This is a piece of evidence."
