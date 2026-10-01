import pytest
from pydantic import ValidationError

from app.models.report import (
    Citation,
    ReportSection,
    ResearchReport,
)


def test_citation_accepts_valid_data():
    citation = Citation(
        citation_id="S1",
        source_id="source-001",
        claim_ids=["claim-001", "claim-002"],
    )

    assert citation.citation_id == "S1"
    assert citation.source_id == "source-001"
    assert citation.claim_ids == ["claim-001", "claim-002"]


def test_citation_rejects_empty_claim_ids():
    with pytest.raises(ValidationError):
        Citation(
            citation_id="S1",
            source_id="source-001",
            claim_ids=[],
        )


def test_report_section_accepts_valid_data():
    section = ReportSection(
        section_id="section-001",
        title="Market Overview",
        content="The market grew during the period.",
        claim_ids=["claim-001"],
    )

    assert section.section_id == "section-001"
    assert section.title == "Market Overview"
    assert section.claim_ids == ["claim-001"]


def test_report_section_defaults_to_empty_claim_ids():
    section = ReportSection(
        section_id="section-001",
        title="Market Overview",
        content="The market grew during the period.",
    )

    assert section.claim_ids == []


def test_report_section_rejects_empty_content():
    with pytest.raises(ValidationError):
        ReportSection(
            section_id="section-001",
            title="Market Overview",
            content="",
        )


def test_research_report_accepts_valid_data():
    report = ResearchReport(
        title="Electric Vehicle Market Research",
        executive_summary="EV registrations increased during the period.",
        sections=[
            ReportSection(
                section_id="section-001",
                title="Market Overview",
                content="The market experienced growth.",
                claim_ids=["claim-001"],
            )
        ],
        citations=[
            Citation(
                citation_id="S1",
                source_id="source-001",
                claim_ids=["claim-001"],
            )
        ],
    )

    assert report.title == "Electric Vehicle Market Research"
    assert len(report.sections) == 1
    assert len(report.citations) == 1


def test_research_report_allows_no_citations():
    report = ResearchReport(
        title="Research Report",
        executive_summary="Summary.",
        sections=[
            ReportSection(
                section_id="section-001",
                title="Introduction",
                content="Introduction content.",
            )
        ],
    )

    assert report.citations == []


def test_research_report_requires_at_least_one_section():
    with pytest.raises(ValidationError):
        ResearchReport(
            title="Research Report",
            executive_summary="Summary.",
            sections=[],
        )
