from app.graph.nodes.gap_checker import ResearchIterationGuard
from app.graph.routing import route_after_gap_check
from app.graph.state import ResearchGraphState
from app.models.research import (
    ResearchPlan,
    ResearchQuestion,
    ResearchQuestionStatus,
    ResearchRequest,
)
from app.models.state import ResearchState


def build_state(
    *,
    iterations: int = 0,
    research_gaps: list[str] | None = None,
    question_statuses: list[ResearchQuestionStatus] | None = None,
) -> ResearchGraphState:
    statuses = question_statuses or [ResearchQuestionStatus.ANSWERED]

    questions = [
        ResearchQuestion(
            id=f"q{i}",
            question=f"Research question {i}",
            priority=1,
            status=status,
        )
        for i, status in enumerate(statuses, start=1)
    ]

    research_state = ResearchState(
        request=ResearchRequest(query="Test research query"),
        plan=ResearchPlan(
            objective="Test objective",
            questions=questions,
        ),
        research_gaps=research_gaps or [],
        iterations=iterations,
    )

    return {"research_state": research_state}


def test_routes_to_report_when_no_gaps_and_no_pending_questions() -> None:
    state = build_state(
        question_statuses=[ResearchQuestionStatus.ANSWERED],
    )

    guard = ResearchIterationGuard(max_iterations=3)

    result = route_after_gap_check(
        state=state,
        iteration_guard=guard,
    )

    assert result == "report"


def test_routes_to_research_when_research_gaps_exist() -> None:
    state = build_state(
        research_gaps=["claim-1"],
        question_statuses=[ResearchQuestionStatus.ANSWERED],
    )

    guard = ResearchIterationGuard(max_iterations=3)

    result = route_after_gap_check(
        state=state,
        iteration_guard=guard,
    )

    assert result == "research"


def test_routes_to_research_when_pending_questions_exist() -> None:
    state = build_state(
        question_statuses=[
            ResearchQuestionStatus.ANSWERED,
            ResearchQuestionStatus.PENDING,
        ],
    )

    guard = ResearchIterationGuard(max_iterations=3)

    result = route_after_gap_check(
        state=state,
        iteration_guard=guard,
    )

    assert result == "research"


def test_routes_to_report_when_iteration_limit_is_reached() -> None:
    state = build_state(
        iterations=3,
        research_gaps=["claim-1"],
        question_statuses=[ResearchQuestionStatus.PENDING],
    )

    guard = ResearchIterationGuard(max_iterations=3)

    result = route_after_gap_check(
        state=state,
        iteration_guard=guard,
    )

    assert result == "report"
