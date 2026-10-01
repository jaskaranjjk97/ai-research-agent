import pytest
from pydantic import ValidationError

from app.models.evidence import Evidence


def test_evidence_accepts_valid_data():
    evidence = Evidence(
        evidence_id="evidence-001",
        source_id="source-001",
        question_id="q1",
        content="EV registrations increased significantly.",
        location="Market Overview, paragraph 3",
    )

    assert evidence.evidence_id == "evidence-001"
    assert evidence.source_id == "source-001"
    assert evidence.question_id == "q1"


def test_evidence_location_is_optional():
    evidence = Evidence(
        evidence_id="evidence-001",
        source_id="source-001",
        question_id="q1",
        content="EV registrations increased significantly.",
    )

    assert evidence.location is None


def test_evidence_requires_content():
    with pytest.raises(ValidationError):
        Evidence(
            evidence_id="evidence-001",
            source_id="source-001",
            question_id="q1",
            content="",
        )
