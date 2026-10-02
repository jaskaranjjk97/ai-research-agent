from datetime import UTC, datetime

import pytest
from pydantic import HttpUrl

from app.models.evidence import Evidence
from app.models.research import ResearchQuestion
from app.models.source import Source
from app.providers.extraction.base import ExtractionProvider
from app.tools.execution import ToolExecutionController, ToolExecutionLimitError
from app.tools.extraction import ExtractionTool


class FakeExtractionProvider(ExtractionProvider):
    """Fake extraction provider for ExtractionTool tests."""

    def __init__(self) -> None:
        self.last_source: Source | None = None
        self.last_question: ResearchQuestion | None = None

    async def extract(
        self, source: Source, question: ResearchQuestion
    ) -> list[Evidence]:

        self.last_source = source.source_id
        self.last_question = question.id

        return [
            Evidence(
                evidence_id="evidence-001",
                source_id=source.source_id,
                question_id=question.id,
                content="This is a piece of evidence.",
                location="Page 1, Paragraph 2",
            )
        ]


def create_source() -> Source:
    return Source(
        source_id="source-001",
        title="EV Market Report",
        url=HttpUrl("https://example.com/report"),
        domain="example.com",
        content="EV adoption increased during the period.",
        source_type="report",
        retrieved_at=datetime.now(UTC),
    )


def create_research_question() -> ResearchQuestion:
    return ResearchQuestion(
        id="question-001",
        question="What are the key findings of this report?",
    )


@pytest.mark.asyncio
async def test_extraction_tool_calls_provider():
    provider = FakeExtractionProvider()

    tool = ExtractionTool(provider=provider)

    source = create_source()
    question = create_research_question()

    evidence_list = await tool.extract(source, question)

    assert len(evidence_list) == 1
    assert evidence_list[0].evidence_id == "evidence-001"
    assert evidence_list[0].source_id == "source-001"
    assert evidence_list[0].question_id == "question-001"
    assert evidence_list[0].content == "This is a piece of evidence."
    assert provider.last_source == "source-001"
    assert provider.last_question == "question-001"


@pytest.mark.asyncio
async def test_extraction_tool_returns_empty_list_when_provider_returns_none():
    class EmptyExtractionProvider(ExtractionProvider):
        async def extract(
            self,
            source: Source,
            question: ResearchQuestion,
        ) -> list[Evidence]:
            return []

    provider = EmptyExtractionProvider()

    tool = ExtractionTool(
        provider=provider,
    )

    evidence = await tool.extract(
        source=create_source(),
        question=create_research_question(),
    )

    assert evidence == []


@pytest.mark.asyncio
async def test_extraction_tool_records_tool_execution():
    provider = FakeExtractionProvider()

    controller = ToolExecutionController(
        max_tool_calls=2,
    )

    tool = ExtractionTool(
        provider=provider,
        tool_execution_controller=controller,
    )

    source = create_source()
    question = create_research_question()

    await tool.extract(
        source=source,
        question=question,
    )

    assert controller.tool_calls == 1


@pytest.mark.asyncio
async def test_extraction_tool_respects_execution_limit():
    provider = FakeExtractionProvider()

    controller = ToolExecutionController(
        max_tool_calls=1,
    )

    tool = ExtractionTool(
        provider=provider,
        tool_execution_controller=controller,
    )

    source = create_source()
    question = create_research_question()

    await tool.extract(
        source=source,
        question=question,
    )

    with pytest.raises(ToolExecutionLimitError):
        await tool.extract(
            source=source,
            question=question,
        )

    assert controller.tool_calls == 1
