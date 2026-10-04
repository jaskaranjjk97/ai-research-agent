from typing import Literal

from app.graph.nodes.gap_checker import ResearchIterationGuard
from app.graph.state import ResearchGraphState
from app.models.research import ResearchQuestionStatus


def route_after_gap_check(
    state: ResearchGraphState,
    iteration_guard: ResearchIterationGuard,
) -> Literal["research", "report"]:
    """Route based on research gaps, pending questions, and iteration limits."""

    research_state = state["research_state"]

    if not iteration_guard.can_continue(research_state.iterations):
        return "report"

    if research_state.research_gaps:
        return "research"

    if research_state.plan is not None:
        has_pending_questions = any(
            question.status == ResearchQuestionStatus.PENDING
            for question in research_state.plan.questions
        )

        if has_pending_questions:
            return "research"

    return "report"
