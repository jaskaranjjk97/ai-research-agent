from datetime import UTC, datetime

import pytest

from app.graph.nodes.citation_validator import citation_validation_node
from app.graph.state import ResearchGraphState
from app.models.claim import Claim
from app.models.report import Citation, ReportSection, ResearchReport
from app.models.source import Source
from app.models.state import ResearchState
from app.verification.citation_validator import CitationValidator


def make_source(source_id: str) -> Source:
    return Source(
        source_id=source_id,
        title="Test Source",
        url="https://example.com",
        domain="example.com",
        content="Test source content.",
        retrieved_at=datetime.now(UTC),
    )


def make_claim(claim_id: str) -> Claim:
    return Claim(
        claim_id=claim_id,
        statement="Test claim",
        evidence_ids=["evidence-1"],
    )


def make_report(
    citations: list[Citation],
) -> ResearchReport:
    return ResearchReport(
        title="Test Report",
        executive_summary="Test summary",
        sections=[
            ReportSection(
                section_id="section-1",
                title="Introduction",
                content="Test content",
                claim_ids=["claim-1"],
            )
        ],
        citations=citations,
    )


def make_state(
    report: ResearchReport | None,
    claims: list[Claim],
    sources: list[Source],
) -> ResearchGraphState:
    research_state = ResearchState(
        request={
            "query": "Test research request",
        },
        report=report,
        claims=claims,
        sources=sources,
    )

    return {
        "research_state": research_state,
    }


@pytest.mark.asyncio
async def test_citation_validation_node_accepts_valid_report() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="source-1",
                claim_ids=["claim-1"],
            )
        ]
    )

    state = make_state(
        report=report,
        claims=[make_claim("claim-1")],
        sources=[make_source("source-1")],
    )

    result = await citation_validation_node(
        state=state,
        citation_validator=CitationValidator(),
    )

    assert result is state
    assert result["research_state"].report == report


@pytest.mark.asyncio
async def test_citation_validation_node_rejects_missing_report() -> None:
    state = make_state(
        report=None,
        claims=[make_claim("claim-1")],
        sources=[make_source("source-1")],
    )

    with pytest.raises(
        ValueError,
        match="Research report is required before citation validation",
    ):
        await citation_validation_node(
            state=state,
            citation_validator=CitationValidator(),
        )


@pytest.mark.asyncio
async def test_citation_validation_node_rejects_invalid_citation() -> None:
    report = make_report(
        citations=[
            Citation(
                citation_id="citation-1",
                source_id="unknown-source",
                claim_ids=["claim-1"],
            )
        ]
    )

    state = make_state(
        report=report,
        claims=[make_claim("claim-1")],
        sources=[make_source("source-1")],
    )

    with pytest.raises(
        ValueError,
        match="unknown source ID",
    ):
        await citation_validation_node(
            state=state,
            citation_validator=CitationValidator(),
        )
