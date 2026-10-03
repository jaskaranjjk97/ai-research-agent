import pytest

from app.graph.nodes.gap_checker import (
    GapChecker,
    ResearchIterationGuard,
    gap_check_node,
)
from app.graph.state import ResearchGraphState
from app.models.claim import (
    Claim,
    VerificationResult,
    VerificationStatus,
)
from app.models.research import ResearchRequest
from app.models.state import ResearchState


def test_gap_checker_returns_no_gaps_for_supported_claims():
    claims = [
        Claim(
            claim_id="c1",
            statement="Supported claim.",
            evidence_ids=["e1"],
            importance=5,
        )
    ]

    verification_results = [
        VerificationResult(
            claim_id="c1",
            status=VerificationStatus.SUPPORTED,
            confidence=0.95,
            evidence_ids=["e1"],
            explanation="Evidence directly supports the claim.",
        )
    ]

    checker = GapChecker()

    gaps = checker.check(
        claims=claims,
        verification_results=verification_results,
    )

    assert gaps == []


def test_gap_checker_detects_not_supported_claim():
    claims = [
        Claim(
            claim_id="c1",
            statement="Unsupported claim.",
            evidence_ids=["e1"],
            importance=3,
        )
    ]

    verification_results = [
        VerificationResult(
            claim_id="c1",
            status=VerificationStatus.NOT_SUPPORTED,
            confidence=0.9,
            evidence_ids=["e1"],
            explanation="Evidence does not support the claim.",
        )
    ]

    checker = GapChecker()

    gaps = checker.check(
        claims=claims,
        verification_results=verification_results,
    )

    assert gaps == ["c1"]


def test_gap_checker_detects_insufficient_evidence():
    claims = [
        Claim(
            claim_id="c1",
            statement="Important claim.",
            evidence_ids=["e1"],
            importance=5,
        )
    ]

    verification_results = [
        VerificationResult(
            claim_id="c1",
            status=VerificationStatus.INSUFFICIENT_EVIDENCE,
            confidence=0.4,
            evidence_ids=["e1"],
            explanation="There is not enough evidence.",
        )
    ]

    checker = GapChecker()

    gaps = checker.check(
        claims=claims,
        verification_results=verification_results,
    )

    assert gaps == ["c1"]


def test_gap_checker_ignores_low_importance_partial_claim():
    claims = [
        Claim(
            claim_id="c1",
            statement="Minor partially supported claim.",
            evidence_ids=["e1"],
            importance=2,
        )
    ]

    verification_results = [
        VerificationResult(
            claim_id="c1",
            status=VerificationStatus.PARTIALLY_SUPPORTED,
            confidence=0.7,
            evidence_ids=["e1"],
            explanation="Only part of the claim is supported.",
        )
    ]

    checker = GapChecker()

    gaps = checker.check(
        claims=claims,
        verification_results=verification_results,
    )

    assert gaps == []


@pytest.mark.asyncio
async def test_gap_check_node_updates_research_gaps():
    claims = [
        Claim(
            claim_id="c1",
            statement="Important claim.",
            evidence_ids=["e1"],
            importance=5,
        )
    ]

    verification_results = [
        VerificationResult(
            claim_id="c1",
            status=VerificationStatus.INSUFFICIENT_EVIDENCE,
            confidence=0.4,
            evidence_ids=["e1"],
            explanation="More evidence is required.",
        )
    ]

    research_state = ResearchState(
        request=ResearchRequest(query="Test research question"),
        claims=claims,
        verification_results=verification_results,
    )

    state: ResearchGraphState = {
        "research_state": research_state,
    }

    checker = GapChecker()

    result = await gap_check_node(
        state=state,
        gap_checker=checker,
    )

    assert result["research_state"].research_gaps == ["c1"]


def test_iteration_guard_allows_iterations_below_limit():
    guard = ResearchIterationGuard(max_iterations=3)

    assert guard.can_continue(0) is True
    assert guard.can_continue(1) is True
    assert guard.can_continue(2) is True


def test_iteration_guard_stops_at_limit():
    guard = ResearchIterationGuard(max_iterations=3)

    assert guard.can_continue(3) is False


def test_iteration_guard_rejects_invalid_limit():
    with pytest.raises(
        ValueError,
        match="Max iterations should atleast be 1.",
    ):
        ResearchIterationGuard(max_iterations=0)


def test_iteration_guard_rejects_negative_iteration():
    guard = ResearchIterationGuard(max_iterations=3)

    with pytest.raises(
        ValueError,
        match="iteration cannot be negative",
    ):
        guard.can_continue(-1)


def test_start_iteration_increments_state() -> None:
    research_state = ResearchState(
        request=ResearchRequest(query="Test research request"),
    )

    guard = ResearchIterationGuard(max_iterations=3)

    assert research_state.iterations == 0

    guard.start_iteration(research_state)

    assert research_state.iterations == 1

    guard.start_iteration(research_state)

    assert research_state.iterations == 2


def test_start_iteration_rejects_when_limit_reached() -> None:
    research_state = ResearchState(
        request=ResearchRequest(query="Test research request"),
        iterations=3,
    )

    guard = ResearchIterationGuard(max_iterations=3)

    with pytest.raises(
        RuntimeError,
        match="Maximum research iteration limit has been reached.",
    ):
        guard.start_iteration(research_state)

    assert research_state.iterations == 3
