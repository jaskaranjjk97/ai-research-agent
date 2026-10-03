import pytest

from app.graph.nodes.extractor import EvidenceExtractor, extractor_node
from app.graph.state import ResearchGraphState
from app.models.evidence import Evidence
from app.models.research import (
    ResearchPlan,
    ResearchQuestion,
    ResearchQuestionStatus,
    ResearchRequest,
)
from app.models.source import SearchResult, Source
from app.models.state import ResearchState
from app.providers.extraction.base import ExtractionProvider
from app.tools.extraction import ExtractionTool


class FakeExtractionProvider(ExtractionProvider):
    """Fake extraction provider for extractor tests."""

    def __init__(
        self,
        evidence: list[Evidence],
    ) -> None:
        self.evidence = evidence
        self.last_source: Source | None = None
        self.last_question: ResearchQuestion | None = None

    async def extract(
        self,
        source: Source,
        question: ResearchQuestion,
    ) -> list[Evidence]:
        self.last_source = source
        self.last_question = question

        return self.evidence


class FakeSourceService:
    """Fake source service for extractor node tests."""

    def __init__(
        self,
        source: Source,
    ) -> None:
        self.source = source
        self.last_search_result: SearchResult | None = None

    async def fetch_source(
        self,
        search_result: SearchResult,
    ) -> Source:
        self.last_search_result = search_result
        return self.source


@pytest.mark.asyncio
async def test_extractor_node_updates_graph_state():
    search_result = SearchResult(
        title="AI Research",
        url="https://example.com/ai",
        snippet="Research information.",
        question_id="q1",
    )

    source = Source(
        source_id="source-1",
        title="AI Research",
        url="https://example.com/ai",
        domain="example.com",
        content="Generative AI is increasingly used in software development.",
        source_type="article",
        retrieved_at="2026-10-03T00:00:00Z",
    )

    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content="Generative AI is increasingly used in software development.",
            location="paragraph 1",
        ),
    ]

    source_service = FakeSourceService(source)

    extraction_provider = FakeExtractionProvider(evidence)

    extraction_tool = ExtractionTool(
        provider=extraction_provider,
    )

    evidence_extractor = EvidenceExtractor(
        extraction_tool=extraction_tool,
    )

    request = ResearchRequest(
        query="Research generative AI adoption.",
    )

    plan = ResearchPlan(
        objective="Research generative AI adoption.",
        questions=[
            ResearchQuestion(
                id="q1",
                question="How is generative AI being adopted?",
                priority=5,
                status=ResearchQuestionStatus.RESEARCHING,
            ),
        ],
    )

    research_state = ResearchState(
        request=request,
        plan=plan,
        current_question_id="q1",
        search_results=[search_result],
    )

    graph_state: ResearchGraphState = {
        "research_state": research_state,
    }

    result = await extractor_node(
        state=graph_state,
        source_service=source_service,
        evidence_extractor=evidence_extractor,
    )

    assert result["research_state"].sources == [source]
    assert result["research_state"].evidences == evidence

    assert source_service.last_search_result == search_result
    assert extraction_provider.last_source == source
    assert extraction_provider.last_question is not None
    assert extraction_provider.last_question.id == "q1"


@pytest.mark.asyncio
async def test_extractor_node_ignores_results_for_other_questions():
    q1_result = SearchResult(
        title="Q1 Result",
        url="https://example.com/q1",
        snippet="Q1 information.",
        question_id="q1",
    )

    q2_result = SearchResult(
        title="Q2 Result",
        url="https://example.com/q2",
        snippet="Q2 information.",
        question_id="q2",
    )

    source = Source(
        source_id="source-1",
        title="Q1 Result",
        url="https://example.com/q1",
        domain="example.com",
        content="Q1 content.",
        source_type="article",
        retrieved_at="2026-10-03T00:00:00Z",
    )

    source_service = FakeSourceService(source)

    extraction_provider = FakeExtractionProvider([])

    evidence_extractor = EvidenceExtractor(
        extraction_tool=ExtractionTool(
            provider=extraction_provider,
        ),
    )

    request = ResearchRequest(
        query="Research AI.",
    )

    plan = ResearchPlan(
        objective="Research AI.",
        questions=[
            ResearchQuestion(
                id="q1",
                question="Question one",
                priority=5,
                status=ResearchQuestionStatus.RESEARCHING,
            ),
        ],
    )

    research_state = ResearchState(
        request=request,
        plan=plan,
        current_question_id="q1",
        search_results=[q1_result, q2_result],
    )

    graph_state: ResearchGraphState = {
        "research_state": research_state,
    }

    await extractor_node(
        state=graph_state,
        source_service=source_service,
        evidence_extractor=evidence_extractor,
    )

    assert source_service.last_search_result == q1_result


@pytest.mark.asyncio
async def test_evidence_extractor_extracts_evidence():
    source = Source(
        source_id="source-1",
        title="Generative AI Report",
        url="https://example.com/report",
        domain="example.com",
        content="Generative AI is increasingly used in software development.",
        source_type="article",
        retrieved_at="2026-10-03T00:00:00Z",
    )

    question = ResearchQuestion(
        id="q1",
        question="How is generative AI being adopted?",
        priority=3,
    )

    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content="Generative AI is increasingly used in software development.",
            location="paragraph 1",
        ),
    ]

    provider = FakeExtractionProvider(
        evidence,
    )

    extraction_tool = ExtractionTool(
        provider=provider,
    )

    extractor = EvidenceExtractor(
        extraction_tool=extraction_tool,
    )

    result = await extractor.extract(
        source=source,
        research_question=question,
    )

    assert result == evidence
    assert provider.last_source == source
    assert provider.last_question == question
