from app.agents.research_agent import ResearchAgent
from app.config.settings import Settings
from app.graph.graph import build_research_graph
from app.graph.nodes.extractor import EvidenceExtractor
from app.graph.nodes.gap_checker import GapChecker, ResearchIterationGuard
from app.graph.nodes.planner import Planner
from app.graph.nodes.reporter import ReportGenerator
from app.graph.nodes.researcher import Researcher
from app.graph.nodes.verifier import ClaimExtractor, ClaimVerifier
from app.providers.extraction.base import ExtractionProvider
from app.providers.factory import create_llm_provider, create_search_provider
from app.providers.llm.base import LLMProvider
from app.providers.search.base import SearchProvider
from app.providers.web.base import WebProvider
from app.providers.web.httpx import HttpxWebProvider
from app.services.research_service import ResearchService
from app.services.source_service import SourceService
from app.tools.execution import ToolExecutionController
from app.tools.extraction import ExtractionTool
from app.tools.search import SearchTool
from app.tools.web_fetch import WebFetchTool
from app.verification.citation_validator import CitationValidator


def build_research_service(
    llm_provider: LLMProvider,
    search_provider: SearchProvider,
    web_provider: WebProvider,
    extraction_provider: ExtractionProvider,
    max_search_results: int = 10,
    max_tool_calls: int = 20,
    max_research_iterations: int = 3,
) -> ResearchService:
    """Build the complete research application dependency graph."""

    tool_execution_controller = ToolExecutionController(
        max_tool_calls=max_tool_calls,
    )

    search_tool = SearchTool(
        provider=search_provider,
        max_results=max_search_results,
        tool_execution_controller=tool_execution_controller,
    )

    web_fetch_tool = WebFetchTool(
        provider=web_provider,
        tool_execution_controller=tool_execution_controller,
    )

    extraction_tool = ExtractionTool(
        provider=extraction_provider,
        tool_execution_controller=tool_execution_controller,
    )

    iteration_guard = ResearchIterationGuard(
        max_iterations=max_research_iterations,
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

    research_agent = ResearchAgent(
        graph=graph,
    )

    return ResearchService(
        research_agent=research_agent,
    )


def build_configured_research_service(
    settings: Settings,
    extraction_provider: ExtractionProvider,
    web_provider: WebProvider | None = None,
) -> ResearchService:
    """Build the research service using application settings."""

    llm_provider = create_llm_provider(settings)
    search_provider = create_search_provider(settings)

    if web_provider is None:
        web_provider = HttpxWebProvider()

    return build_research_service(
        llm_provider=llm_provider,
        search_provider=search_provider,
        web_provider=web_provider,
        extraction_provider=extraction_provider,
        max_search_results=settings.max_search_results,
        max_tool_calls=settings.max_tool_calls,
        max_research_iterations=settings.max_research_iterations,
    )
