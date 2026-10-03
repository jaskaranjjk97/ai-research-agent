from app.graph.nodes.gap_checker import ResearchIterationGuard
from app.graph.routing import route_after_gap_check
from app.graph.state import ResearchGraphState
from app.models.research import ResearchRequest
from app.models.state import ResearchState


def test_route_to_research_when_gaps_exist_and_iteration_available():
    research_state = ResearchState(
        request=ResearchRequest(query="Test research question"),
        research_gaps=["c1"],
        iterations=0,
    )

    state: ResearchGraphState = {
        "research_state": research_state,
    }

    guard = ResearchIterationGuard(max_iterations=3)

    result = route_after_gap_check(
        state=state,
        iteration_guard=guard,
    )

    assert result == "research"


def test_route_to_report_when_no_gaps_exist():
    research_state = ResearchState(
        request=ResearchRequest(query="Test research question"),
        research_gaps=[],
        iterations=0,
    )

    state: ResearchGraphState = {
        "research_state": research_state,
    }

    guard = ResearchIterationGuard(max_iterations=3)

    result = route_after_gap_check(
        state=state,
        iteration_guard=guard,
    )

    assert result == "report"


def test_route_to_report_when_iteration_limit_is_reached():
    research_state = ResearchState(
        request=ResearchRequest(query="Test research question"),
        research_gaps=["c1"],
        iterations=3,
    )

    state: ResearchGraphState = {
        "research_state": research_state,
    }

    guard = ResearchIterationGuard(max_iterations=3)

    result = route_after_gap_check(
        state=state,
        iteration_guard=guard,
    )

    assert result == "report"
