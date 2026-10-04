from datetime import UTC, datetime

from app.graph.graph import build_research_graph
from app.graph.nodes.extractor import EvidenceExtractor
from app.graph.nodes.gap_checker import GapChecker, ResearchIterationGuard
from app.graph.nodes.planner import Planner
from app.graph.nodes.reporter import ReportGenerator
from app.graph.nodes.researcher import Researcher
from app.graph.nodes.verifier import ClaimExtractor, ClaimVerifier
from app.models.claim import VerificationResult
from app.models.evidence import Evidence
from app.models.report import ResearchReport
from app.models.research import ResearchRequest
from app.models.source import SearchResult, Source
from app.models.state import ResearchState
from app.providers.extraction.base import ExtractionProvider
from app.providers.llm.base import LLMProvider
from app.providers.search.base import SearchProvider
from app.providers.web.base import WebProvider
from app.services.source_service import SourceService
from app.tools.extraction import ExtractionTool
from app.tools.search import SearchTool
from app.tools.web_fetch import WebFetchTool
from app.verification.citation_validator import CitationValidator


class FakeLLMProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        normalized_prompt = " ".join(prompt.lower().split())

        if "create a structured research plan" in normalized_prompt:
            return """
            {
                "objective": "Evaluate the test topic.",
                "questions": [
                    {
                        "id": "q1",
                        "question": "What is the main fact about the test topic?",
                        "priority": 5,
                        "status": "pending"
                    }
                ]
            }
            """

        if (
            "extract factual claims" in normalized_prompt
            and "research question" in normalized_prompt
        ):
            return """
            [
                {
                    "claim_id": "claim-1",
                    "statement": "The test topic has a documented primary fact.",
                    "evidence_ids": ["evidence-1"],
                    "importance": 3
                }
            ]
            """

        if "verify the following factual claim" in normalized_prompt:
            return """
            {
                "claim_id": "claim-1",
                "status": "supported",
                "confidence": 0.95,
                "evidence_ids": ["evidence-1"],
                "explanation": "The evidence directly supports the claim."
            }
            """

        if "research report" in normalized_prompt:
            return """
            {
                "title": "Test Research Report",
                "executive_summary": "The research was successfully completed.",
                "sections": [
                    {
                        "section_id": "section-1",
                        "title": "Findings",
                        "content": "The test topic has a documented primary fact.",
                        "claim_ids": ["claim-1"]
                    }
                ],
                "citations": [
                    {
                        "citation_id": "citation-1",
                        "source_id": "source-1",
                        "claim_ids": ["claim-1"]
                    }
                ]
            }
            """

        raise AssertionError(f"Unexpected LLM prompt: {prompt}")


class FakeSearchProvider(SearchProvider):
    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                title="Test Source",
                url="https://example.com/test",
                snippet="The test topic has a documented primary fact.",
                source_name="Example",
            )
        ]


class FakeWebProvider(WebProvider):
    async def fetch(self, url: str) -> Source:
        return Source(
            source_id="source-1",
            title="Test Source",
            url=url,
            domain="example.com",
            content="The test topic has a documented primary fact.",
            source_type="web",
            published_at=None,
            retrieved_at=datetime.now(UTC),
        )


class FakeExtractionProvider(ExtractionProvider):
    async def extract(
        self,
        source: Source,
        question,
    ) -> list[Evidence]:
        return [
            Evidence(
                evidence_id="evidence-1",
                source_id=source.source_id,
                question_id=question.id,
                content="The test topic has a documented primary fact.",
                location="paragraph 1",
            )
        ]


async def test_research_graph_executes_end_to_end() -> None:
    llm_provider = FakeLLMProvider()
    search_provider = FakeSearchProvider()
    web_provider = FakeWebProvider()
    extraction_provider = FakeExtractionProvider()

    search_tool = SearchTool(
        provider=search_provider,
        max_results=10,
    )

    web_fetch_tool = WebFetchTool(
        provider=web_provider,
    )

    extraction_tool = ExtractionTool(
        provider=extraction_provider,
    )

    iteration_guard = ResearchIterationGuard(
        max_iterations=3,
    )

    planner = Planner(
        llm_provider=llm_provider,
    )

    researcher = Researcher(
        search_tool=search_tool,
        iteration_guard=iteration_guard,
    )

    source_service = SourceService(
        web_fetch_tool=web_fetch_tool,
    )

    evidence_extractor = EvidenceExtractor(
        extraction_tool=extraction_tool,
    )

    claim_extractor = ClaimExtractor(
        llm_provider=llm_provider,
    )

    claim_verifier = ClaimVerifier(
        llm_provider=llm_provider,
    )

    gap_checker = GapChecker()

    report_generator = ReportGenerator(
        llm_provider=llm_provider,
    )

    citation_validator = CitationValidator()

    graph = build_research_graph(
        planner=planner,
        researcher=researcher,
        source_service=source_service,
        evidence_extractor=evidence_extractor,
        claim_extractor=claim_extractor,
        claim_verifier=claim_verifier,
        gap_checker=gap_checker,
        iteration_guard=iteration_guard,
        report_generator=report_generator,
        citation_validator=citation_validator,
    )

    initial_state = ResearchState(
        request=ResearchRequest(
            query="What is the test topic?",
        )
    )

    result = await graph.ainvoke(
        {
            "research_state": initial_state,
        }
    )

    research_state = result["research_state"]

    assert research_state.plan is not None
    assert len(research_state.plan.questions) == 1

    assert len(research_state.search_results) == 1

    assert len(research_state.sources) == 1
    assert research_state.sources[0].source_id == "source-1"

    assert len(research_state.evidences) == 1
    assert research_state.evidences[0].evidence_id == "evidence-1"

    assert len(research_state.claims) == 1
    assert research_state.claims[0].claim_id == "claim-1"

    assert len(research_state.verification_results) == 1

    verification = research_state.verification_results[0]

    assert isinstance(verification, VerificationResult)
    assert verification.status == "supported"

    assert research_state.research_gaps == []

    assert research_state.report is not None
    assert isinstance(research_state.report, ResearchReport)

    assert len(research_state.report.citations) == 1

    assert research_state.iterations == 1
