from unittest.mock import MagicMock

from app.graph.graph import build_research_graph
from app.graph.nodes.extractor import EvidenceExtractor
from app.graph.nodes.gap_checker import GapChecker, ResearchIterationGuard
from app.graph.nodes.planner import Planner
from app.graph.nodes.reporter import ReportGenerator
from app.graph.nodes.researcher import Researcher
from app.graph.nodes.verifier import ClaimExtractor, ClaimVerifier
from app.services.source_service import SourceService
from app.verification.citation_validator import CitationValidator


def test_build_research_graph() -> None:
    llm_provider = MagicMock()
    search_tool = MagicMock()
    extraction_tool = MagicMock()
    web_fetch_tool = MagicMock()

    planner = Planner(llm_provider=llm_provider)

    iteration_guard = ResearchIterationGuard(
        max_iterations=3,
    )

    researcher = Researcher(
        search_tool=search_tool,
        iteration_guard=iteration_guard,
    )

    evidence_extractor = EvidenceExtractor(
        extraction_tool=extraction_tool,
    )

    source_service = SourceService(
        web_fetch_tool=web_fetch_tool,
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

    assert graph is not None
