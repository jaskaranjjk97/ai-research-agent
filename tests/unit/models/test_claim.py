import pytest
from pydantic import ValidationError

from app.models.claim import (
    Claim,
    VerificationResult,
    VerificationStatus,
)


def test_claim_accepts_valid_data():
    claim = Claim(
        claim_id="claim-001",
        evidence_ids=["evidence-001"],
        statement="EV registrations increased significantly.",
        importance=4,
    )

    assert claim.claim_id == "claim-001"
    assert claim.evidence_ids == ["evidence-001"]
    assert claim.importance == 4


def test_claim_accepts_default_importance():
    claim = Claim(
        claim_id="claim-002",
        evidence_ids=["evidence-002"],
        statement="EV registrations decreased.",
    )

    assert claim.importance == 3


def test_claim_rejects_empty_evidence_id():
    with pytest.raises(ValidationError):
        Claim(
            claim_id="001",
            evidence_ids=[],
            statement="this is empty evidence_id test",
        )


def test_claim_rejects_invalid_importance():
    with pytest.raises(ValidationError):
        Claim(
            claim_id="claim-003",
            evidence_ids=["evidence-003"],
            statement="EV registrations remained stable.",
            importance=6,
        )


def test_verification_result_accepts_valid_data():
    result = VerificationResult(
        claim_id="claim-1",
        status=VerificationStatus.SUPPORTED,
        confidence=0.95,
        evidence_ids=["evidence-1"],
        explanation="The evidence directly supports the claim.",
    )

    assert result.status == VerificationStatus.SUPPORTED
    assert result.confidence == 0.95


def test_verification_result_accepts_all_statuses():
    for status in VerificationStatus:
        result = VerificationResult(
            claim_id="claim-1",
            status=status,
            confidence=0.5,
            evidence_ids=["evidence-1"],
            explanation="Verification explanation.",
        )

        assert result.status == status


def test_verification_result_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        VerificationResult(
            claim_id="claim-1",
            status=VerificationStatus.SUPPORTED,
            confidence=1.5,
            evidence_ids=["evidence-1"],
            explanation="Verification explanation.",
        )


def test_verification_result_rejects_empty_evidence_id():
    with pytest.raises(ValidationError):
        VerificationResult(
            claim_id="claim-1",
            status=VerificationStatus.SUPPORTED,
            confidence=0.80,
            evidence_ids=[],
            explanation="verification explanation",
        )
