from langgraph.graph import END, START, StateGraph

from app.graph.nodes.citation_validator import citation_validation_node
from app.graph.nodes.extractor import EvidenceExtractor, extractor_node
from app.graph.nodes.gap_checker import (
    GapChecker,
    ResearchIterationGuard,
    gap_check_node,
)
from app.graph.nodes.planner import Planner, planner_node
from app.graph.nodes.reporter import ReportGenerator, reporter_node
from app.graph.nodes.researcher import Researcher, researcher_node
from app.graph.nodes.verifier import (
    ClaimExtractor,
    ClaimVerifier,
    verifier_node,
)
from app.graph.routing import route_after_gap_check
from app.graph.state import ResearchGraphState
from app.services.source_service import SourceService
from app.verification.citation_validator import CitationValidator


def build_research_graph(
    planner: Planner,
    researcher: Researcher,
    source_service: SourceService,
    evidence_extractor: EvidenceExtractor,
    claim_extractor: ClaimExtractor,
    claim_verifier: ClaimVerifier,
    gap_checker: GapChecker,
    iteration_guard: ResearchIterationGuard,
    report_generator: ReportGenerator,
    citation_validator: CitationValidator,
):
    """Build and compile the autonomous research workflow."""

    graph = StateGraph(ResearchGraphState)

    async def planner_node_wrapper(
        state: ResearchGraphState,
    ) -> ResearchGraphState:
        return await planner_node(
            state=state,
            planner=planner,
        )

    async def researcher_node_wrapper(
        state: ResearchGraphState,
    ) -> ResearchGraphState:
        return await researcher_node(
            state=state,
            researcher=researcher,
        )

    async def extractor_node_wrapper(
        state: ResearchGraphState,
    ) -> ResearchGraphState:
        return await extractor_node(
            state=state,
            source_service=source_service,
            evidence_extractor=evidence_extractor,
        )

    async def verifier_node_wrapper(
        state: ResearchGraphState,
    ) -> ResearchGraphState:
        return await verifier_node(
            state=state,
            claim_extractor=claim_extractor,
            claim_verifier=claim_verifier,
        )

    async def gap_check_node_wrapper(
        state: ResearchGraphState,
    ) -> ResearchGraphState:
        return await gap_check_node(
            state=state,
            gap_checker=gap_checker,
        )

    async def reporter_node_wrapper(
        state: ResearchGraphState,
    ) -> ResearchGraphState:
        return await reporter_node(
            state=state,
            report_generator=report_generator,
        )

    async def citation_validation_node_wrapper(
        state: ResearchGraphState,
    ) -> ResearchGraphState:
        return await citation_validation_node(
            state=state,
            citation_validator=citation_validator,
        )

    graph.add_node(
        "planner",
        planner_node_wrapper,
    )

    graph.add_node(
        "research",
        researcher_node_wrapper,
    )

    graph.add_node(
        "extract",
        extractor_node_wrapper,
    )

    graph.add_node(
        "verify",
        verifier_node_wrapper,
    )

    graph.add_node(
        "gap_check",
        gap_check_node_wrapper,
    )

    graph.add_node(
        "report",
        reporter_node_wrapper,
    )

    graph.add_node(
        "citation_validation",
        citation_validation_node_wrapper,
    )

    graph.add_edge(
        START,
        "planner",
    )

    graph.add_edge(
        "planner",
        "research",
    )

    graph.add_edge(
        "research",
        "extract",
    )

    graph.add_edge(
        "extract",
        "verify",
    )

    graph.add_edge(
        "verify",
        "gap_check",
    )

    def route(state: ResearchGraphState) -> str:
        return route_after_gap_check(
            state=state,
            iteration_guard=iteration_guard,
        )

    graph.add_conditional_edges(
        "gap_check",
        route,
        {
            "research": "research",
            "report": "report",
        },
    )

    graph.add_edge(
        "report",
        "citation_validation",
    )

    graph.add_edge(
        "citation_validation",
        END,
    )

    return graph.compile()
