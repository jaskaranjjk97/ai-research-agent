from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.graph.nodes.reporter import ReportGenerator, reporter_node
from app.models.claim import Claim, VerificationResult, VerificationStatus
from app.models.evidence import Evidence
from app.models.report import ResearchReport
from app.models.research import ResearchPlan, ResearchQuestion, ResearchRequest
from app.models.source import Source
from app.models.state import ResearchState


class FakeLLMProvider:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def make_claim(claim_id: str, importance: int = 3) -> Claim:
    return Claim(
        claim_id=claim_id,
        statement=f"Statement for {claim_id}",
        evidence_ids=["evidence-1"],
        importance=importance,
    )


def make_verification(
    claim_id: str,
    status: VerificationStatus,
) -> VerificationResult:
    return VerificationResult(
        claim_id=claim_id,
        status=status,
        confidence=0.9,
        evidence_ids=["evidence-1"],
        explanation=f"Verification for {claim_id}",
    )


def test_select_usable_claims_returns_supported_claims() -> None:
    claims = [
        make_claim("claim-1"),
        make_claim("claim-2"),
    ]

    verification_results = [
        make_verification("claim-1", VerificationStatus.SUPPORTED),
        make_verification("claim-2", VerificationStatus.NOT_SUPPORTED),
    ]

    result = ReportGenerator._select_usable_claims(
        claims=claims,
        verification_results=verification_results,
    )

    assert result == [claims[0]]


def test_select_usable_claims_returns_partially_supported_claims() -> None:
    claims = [
        make_claim("claim-1"),
        make_claim("claim-2"),
    ]

    verification_results = [
        make_verification(
            "claim-1",
            VerificationStatus.PARTIALLY_SUPPORTED,
        ),
        make_verification(
            "claim-2",
            VerificationStatus.NOT_SUPPORTED,
        ),
    ]

    result = ReportGenerator._select_usable_claims(
        claims=claims,
        verification_results=verification_results,
    )

    assert result == [claims[0]]


def test_select_usable_claims_excludes_not_supported_claims() -> None:
    claims = [
        make_claim("claim-1"),
        make_claim("claim-2"),
    ]

    verification_results = [
        make_verification(
            "claim-1",
            VerificationStatus.NOT_SUPPORTED,
        ),
        make_verification(
            "claim-2",
            VerificationStatus.SUPPORTED,
        ),
    ]

    result = ReportGenerator._select_usable_claims(
        claims=claims,
        verification_results=verification_results,
    )

    assert result == [claims[1]]


def test_select_usable_claims_excludes_insufficient_evidence() -> None:
    claims = [
        make_claim("claim-1"),
        make_claim("claim-2"),
    ]

    verification_results = [
        make_verification(
            "claim-1",
            VerificationStatus.INSUFFICIENT_EVIDENCE,
        ),
        make_verification(
            "claim-2",
            VerificationStatus.SUPPORTED,
        ),
    ]

    result = ReportGenerator._select_usable_claims(
        claims=claims,
        verification_results=verification_results,
    )

    assert result == [claims[1]]


def test_select_usable_claims_excludes_unverified_claims() -> None:
    claims = [
        make_claim("claim-1"),
        make_claim("claim-2"),
    ]

    verification_results = [
        make_verification(
            "claim-1",
            VerificationStatus.SUPPORTED,
        ),
    ]

    result = ReportGenerator._select_usable_claims(
        claims=claims,
        verification_results=verification_results,
    )

    assert result == [claims[0]]


def test_build_prompt_contains_research_objective() -> None:
    plan = ResearchPlan(
        objective="Understand the impact of generative AI.",
        questions=[
            ResearchQuestion(
                id="q1",
                question="What is generative AI?",
            ),
        ],
    )

    claims = [make_claim("claim-1")]

    evidence = [
        Evidence(
            evidence_id="evidence-1",
            source_id="source-1",
            question_id="q1",
            content="Generative AI refers to models that generate new content.",
        ),
    ]

    sources = [
        Source(
            source_id="source-1",
            title="Generative AI Report",
            url="https://example.com/report",
            domain="example.com",
            content="Full source content.",
            retrieved_at=datetime.now(UTC),
        ),
    ]

    prompt = ReportGenerator._build_prompt(
        plan=plan,
        claims=claims,
        evidence=evidence,
        sources=sources,
    )

    assert "Understand the impact of generative AI." in prompt
    assert "claim-1" in prompt
    assert "evidence-1" in prompt
    assert "source-1" in prompt


def test_build_prompt_contains_report_schema_requirements() -> None:
    plan = ResearchPlan(
        objective="Research generative AI.",
        questions=[
            ResearchQuestion(
                id="q1",
                question="What is generative AI?",
            ),
        ],
    )

    prompt = ReportGenerator._build_prompt(
        plan=plan,
        claims=[make_claim("claim-1")],
        evidence=[],
        sources=[],
    )

    assert "title" in prompt
    assert "executive_summary" in prompt
    assert "sections" in prompt
    assert "citations" in prompt
    assert "claim_ids" in prompt
    assert "source_id" in prompt


@pytest.mark.asyncio
async def test_generate_returns_research_report() -> None:
    response = """
    {
        "title": "Generative AI Research",
        "executive_summary":
         "Generative AI is a class of AI systems capable of creating new content.",
        "sections": [
            {
                "section_id": "section-1",
                "title": "Overview",
                "content": "Generative AI systems can produce new content.",
                "claim_ids": ["claim-1"]
            }
        ],
        "citations": [
            {
                "citation_id": "citation-1",
                "source_id": "source-1",
                "claim_ids": ["claim-1"]
            }
        ]
    }
    """

    provider = FakeLLMProvider(response)

    generator = ReportGenerator(
        llm_provider=provider,
    )

    plan = ResearchPlan(
        objective="Research generative AI.",
        questions=[
            ResearchQuestion(
                id="q1",
                question="What is generative AI?",
            ),
        ],
    )

    claims = [
        make_claim("claim-1"),
        make_claim("claim-2"),
    ]

    verification_results = [
        make_verification(
            "claim-1",
            VerificationStatus.SUPPORTED,
        ),
        make_verification(
            "claim-2",
            VerificationStatus.NOT_SUPPORTED,
        ),
    ]

    evidence = [
        Evidence(
            evidence_id="evidence-1",
            source_id="source-1",
            question_id="q1",
            content="Generative AI can create new content.",
        ),
    ]

    sources = [
        Source(
            source_id="source-1",
            title="Generative AI Report",
            url="https://example.com/report",
            domain="example.com",
            content="Full source content.",
            retrieved_at=datetime.now(UTC),
        ),
    ]

    result = await generator.generate(
        plan=plan,
        claims=claims,
        verification_results=verification_results,
        evidence=evidence,
        sources=sources,
    )

    assert isinstance(result, ResearchReport)
    assert result.title == "Generative AI Research"
    assert result.sections[0].claim_ids == ["claim-1"]
    assert result.citations[0].source_id == "source-1"
    assert len(provider.prompts) == 1
    assert "claim-1" in provider.prompts[0]
    assert "claim-2" not in provider.prompts[0]


@pytest.mark.asyncio
async def test_reporter_node_stores_generated_report() -> None:
    plan = ResearchPlan(
        objective="Research generative AI.",
        questions=[
            ResearchQuestion(
                id="q1",
                question="What is generative AI?",
            ),
        ],
    )

    research_state = ResearchState(
        request=ResearchRequest(query="Research generative AI."),
        plan=plan,
    )

    expected_report = ResearchReport(
        title="Generative AI Research",
        executive_summary="A research summary.",
        sections=[
            {
                "section_id": "section-1",
                "title": "Overview",
                "content": "Generative AI can generate new content.",
                "claim_ids": [],
            }
        ],
        citations=[],
    )

    report_generator = Mock()
    report_generator.generate = AsyncMock(return_value=expected_report)

    state = {"research_state": research_state}

    result = await reporter_node(
        state=state,
        report_generator=report_generator,
    )

    assert result["research_state"].report == expected_report
    report_generator.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_reporter_node_requires_research_plan() -> None:
    research_state = ResearchState(
        request=ResearchRequest(query="Research generative AI."),
    )

    report_generator = Mock()

    state = {"research_state": research_state}

    with pytest.raises(
        ValueError,
        match="Research plan is required before running the reporter node.",
    ):
        await reporter_node(
            state=state,
            report_generator=report_generator,
        )

    report_generator.generate.assert_not_called()
