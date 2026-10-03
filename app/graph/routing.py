from typing import Literal

from app.graph.nodes.gap_checker import ResearchIterationGuard
from app.graph.state import ResearchGraphState


def route_after_gap_check(
    state: ResearchGraphState,
    iteration_guard: ResearchIterationGuard,
) -> Literal["research", "report"]:
    """Route based on research gaps and iteration limits."""

    research_state = state["research_state"]

    if not research_state.research_gaps:
        return "report"

    if iteration_guard.can_continue(research_state.iterations):
        return "research"

    return "report"
