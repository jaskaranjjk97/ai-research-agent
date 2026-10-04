from datetime import UTC, datetime

import pytest

from app.models.claim import Claim
from app.models.report import Citation, ReportSection, ResearchReport
from app.models.source import Source
from app.verification.citation_validator import CitationValidator


def make_claim(claim_id: str) -> Claim:
    return Claim(
        claim_id=claim_id,
        statement=f"Statement for {claim_id}",
        evidence_ids=["evidence-1"],
    )


def make_source(source_id: str) -> Source:
    return Source(
        source_id=source_id,
        title=f"Source {source_id}",
        url="https://example.com/source",
        domain="example.com",
        content="Source content.",
        retrieved_at=datetime.now(UTC),
    )


def make_report(citations: list[Citation]) -> ResearchReport:
    return ResearchReport(
        title="Test Research Report",
        executive_summary="Test summary.",
        sections=[
            ReportSection(
                section_id="section-1",
                title="Overview",
                content="Test content.",
                claim_ids=["claim-1"],
            )
        ],
        citations=citations,
    )


def test_validator_accepts_valid_citations() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["claim-1"],
            )
        ]
    )

    claims = [make_claim("claim-1")]
    sources = [make_source("source-1")]

    result = CitationValidator.validate(
        report=report,
        claims=claims,
        sources=sources,
    )

    assert result == report


def test_validator_accepts_multiple_claims_for_one_citation() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["claim-1", "claim-2"],
            )
        ]
    )

    claims = [
        make_claim("claim-1"),
        make_claim("claim-2"),
    ]

    sources = [make_source("source-1")]

    result = CitationValidator.validate(
        report=report,
        claims=claims,
        sources=sources,
    )

    assert result == report


def test_validator_rejects_unknown_source() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="unknown-source",
                claim_ids=["claim-1"],
            )
        ]
    )

    claims = [make_claim("claim-1")]
    sources = [make_source("source-1")]

    with pytest.raises(
        ValueError,
        match="references unknown source ID",
    ):
        CitationValidator.validate(
            report=report,
            claims=claims,
            sources=sources,
        )


def test_validator_rejects_unknown_claim() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["unknown-claim"],
            )
        ]
    )

    claims = [make_claim("claim-1")]
    sources = [make_source("source-1")]

    with pytest.raises(
        ValueError,
        match="references unknown claim IDs",
    ):
        CitationValidator.validate(
            report=report,
            claims=claims,
            sources=sources,
        )


def test_validator_rejects_when_one_claim_is_unknown() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["claim-1", "unknown-claim"],
            )
        ]
    )

    claims = [make_claim("claim-1")]
    sources = [make_source("source-1")]

    with pytest.raises(
        ValueError,
        match="unknown claim IDs",
    ):
        CitationValidator.validate(
            report=report,
            claims=claims,
            sources=sources,
        )
