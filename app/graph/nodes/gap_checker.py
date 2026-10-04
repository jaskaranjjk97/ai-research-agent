from app.graph.state import ResearchGraphState
from app.models.claim import (
    Claim,
    VerificationResult,
    VerificationStatus,
)
from app.models.research import ResearchQuestionStatus
from app.models.state import ResearchState


class GapChecker:
    """Identifies unresolved research gaps from verification results."""

    def check(
        self,
        claims: list[Claim],
        verification_results: list[VerificationResult],
    ) -> list[str]:
        """Return claim IDs that represent unresolved research gaps."""

        claims_by_id = {claim.claim_id: claim for claim in claims}

        latest_results = {result.claim_id: result for result in verification_results}

        gaps: list[str] = []

        for claim_id, result in latest_results.items():
            claim = claims_by_id.get(claim_id)

            if claim is None:
                continue

            if result.status in {
                VerificationStatus.NOT_SUPPORTED,
                VerificationStatus.INSUFFICIENT_EVIDENCE,
            }:
                gaps.append(claim_id)
                continue

            if (
                result.status == VerificationStatus.PARTIALLY_SUPPORTED
                and claim.importance >= 4
            ):
                gaps.append(claim_id)

        return gaps


async def gap_check_node(
    state: ResearchGraphState,
    gap_checker: GapChecker,
) -> ResearchGraphState:
    """Check whether the current research has unresolved gaps."""

    research_state = state["research_state"]

    gaps = gap_checker.check(
        claims=research_state.claims,
        verification_results=research_state.verification_results,
    )

    research_state.research_gaps = gaps

    if research_state.plan is not None:
        current_question = next(
            (
                question
                for question in research_state.plan.questions
                if question.id == research_state.current_question_id
            ),
            None,
        )

        if current_question is not None:
            if gaps:
                current_question.status = ResearchQuestionStatus.PENDING
            else:
                current_question.status = ResearchQuestionStatus.ANSWERED

    return state


class ResearchIterationGuard:
    """Prevents infinite loops for research-gap-research."""

    def __init__(self, max_iterations: int) -> None:
        if max_iterations < 1:
            raise ValueError("Max iterations should atleast be 1.")
        self.max_iterations = max_iterations

    def can_continue(self, iteration: int) -> bool:
        """Return whether another research iteration is allowed."""

        if iteration < 0:
            raise ValueError("iteration cannot be negative.")

        return iteration < self.max_iterations

    def start_iteration(self, research_state: ResearchState) -> None:
        """Start the next research iteration if the limit allows it."""

        if not self.can_continue(research_state.iterations):
            raise RuntimeError("Maximum research iteration limit has been reached.")

        research_state.iterations += 1
