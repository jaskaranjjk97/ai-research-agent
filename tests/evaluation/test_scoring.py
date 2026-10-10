from datetime import UTC, datetime

import pytest

from app.models.claim import Claim
from app.models.report import Citation, ReportSection, ResearchReport
from app.models.source import Source
from tests.evaluation.scoring import evaluate_report


def make_claim(claim_id: str) -> Claim:
    return Claim(
        claim_id=claim_id,
        evidence_ids=["evidence-1"],
        statement=f"Statement for {claim_id}",
    )


def make_source(source_id: str = "source-1") -> Source:
    return Source(
        source_id=source_id,
        title="Example Research Source",
        url="https://example.com/research",
        domain="example.com",
        content="Example source content.",
        retrieved_at=datetime.now(UTC),
    )


def make_report(
    citations: list[Citation] | None = None,
    section_titles: list[str] | None = None,
) -> ResearchReport:
    titles = section_titles or ["Overview"]

    return ResearchReport(
        title="Research Evaluation",
        executive_summary="Summary of the research findings.",
        sections=[
            ReportSection(
                section_id=f"section-{index}",
                title=title,
                content=f"Content for {title}.",
                claim_ids=["claim-1"],
            )
            for index, title in enumerate(titles, start=1)
        ],
        citations=citations or [],
    )


def test_evaluate_report_returns_perfect_scores() -> None:
    claims = [make_claim("claim-1"), make_claim("claim-2")]

    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["claim-1", "claim-2"],
            )
        ],
        section_titles=["Overview", "Conclusion"],
    )

    score = evaluate_report(
        report=report,
        claims=claims,
        sources=[make_source()],
        expected_sections=["Overview", "Conclusion"],
    )

    assert score.citation_integrity == 1.0
    assert score.claim_citation_coverage == 1.0
    assert score.section_coverage == 1.0


def test_evaluate_report_calculates_claim_citation_coverage() -> None:
    claims = [make_claim("claim-1"), make_claim("claim-2")]

    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["claim-1"],
            )
        ]
    )

    score = evaluate_report(
        report=report,
        claims=claims,
        sources=[make_source()],
        expected_sections=["Overview"],
    )

    assert score.claim_citation_coverage == 0.5


def test_evaluate_report_calculates_section_coverage() -> None:
    report = make_report(section_titles=["Overview", "Conclusion"])

    score = evaluate_report(
        report=report,
        claims=[],
        sources=[make_source()],
        expected_sections=["Overview", "Conclusion", "Limitations"],
    )

    assert score.section_coverage == pytest.approx(2 / 3)


def test_evaluate_report_matches_section_titles_case_insensitively() -> None:
    report = make_report(section_titles=["OVERVIEW"])

    score = evaluate_report(
        report=report,
        claims=[],
        sources=[make_source()],
        expected_sections=["Overview"],
    )

    assert score.section_coverage == 1.0


def test_evaluate_report_rejects_unknown_source() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="unknown-source",
                claim_ids=["claim-1"],
            )
        ]
    )

    with pytest.raises(ValueError, match="unknown source ID"):
        evaluate_report(
            report=report,
            claims=[make_claim("claim-1")],
            sources=[make_source()],
            expected_sections=["Overview"],
        )


def test_evaluate_report_rejects_unknown_claim() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["unknown-claim"],
            )
        ]
    )

    with pytest.raises(ValueError, match="unknown claim IDs"):
        evaluate_report(
            report=report,
            claims=[make_claim("claim-1")],
            sources=[make_source()],
            expected_sections=["Overview"],
        )


def test_evaluate_report_handles_no_claims() -> None:
    score = evaluate_report(
        report=make_report(),
        claims=[],
        sources=[make_source()],
        expected_sections=["Overview"],
    )

    assert score.claim_citation_coverage is None


def test_evaluation_score_can_be_converted_to_dictionary() -> None:
    score = evaluate_report(
        report=make_report(),
        claims=[make_claim("claim-1")],
        sources=[make_source()],
        expected_sections=["Overview"],
    )

    result = score.to_dict()

    assert result == {
        "citation_integrity": 1.0,
        "claim_citation_coverage": 0.0,
        "section_coverage": 1.0,
    }


def test_evaluate_report_rejects_invalid_source_reference() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-invalid",
                source_id="missing-source",
                claim_ids=["claim-1"],
            )
        ]
    )

    with pytest.raises(ValueError, match="unknown source ID"):
        evaluate_report(
            report=report,
            claims=[make_claim("claim-1")],
            sources=[make_source("source-1")],
            expected_sections=["Overview"],
        )
