import pytest

from app.graph.nodes.verifier import (
    ClaimEvidenceValidator,
    ClaimExtractor,
    ClaimVerifier,
    VerificationEvidenceValidator,
    verifier_node,
)
from app.graph.state import ResearchGraphState
from app.models.claim import Claim, VerificationResult
from app.models.evidence import Evidence
from app.models.research import ResearchPlan, ResearchQuestion, ResearchRequest
from app.models.state import ResearchState
from app.providers.llm.base import LLMProvider


class FakeLLMProvider(LLMProvider):
    """Fake LLM provider for claim extraction tests."""

    def __init__(
        self,
        response: str,
    ) -> None:
        self.response = response
        self.last_prompt: str | None = None

    async def generate(
        self,
        prompt: str,
    ) -> str:
        self.last_prompt = prompt
        return self.response


@pytest.mark.asyncio
async def test_claim_extractor_creates_claims_from_evidence():
    response = """
    [
        {
            "claim_id": "c1",
            "statement": "Generative AI is increasingly used in software development.",
            "evidence_ids": ["e1"],
            "importance": 4
        }
    ]
    """

    provider = FakeLLMProvider(response)

    extractor = ClaimExtractor(
        llm_provider=provider,
    )

    question = ResearchQuestion(
        id="q1",
        question="How is generative AI being adopted?",
        priority=3,
    )

    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content=("Generative AI is increasingly used in software development."),
        ),
    ]

    claims = await extractor.extract_claims(
        evidence=evidence,
        question=question,
    )

    assert len(claims) == 1
    assert claims[0].claim_id == "c1"
    assert (
        claims[0].statement
        == "Generative AI is increasingly used in software development."
    )
    assert claims[0].evidence_ids == ["e1"]
    assert claims[0].importance == 4

    assert provider.last_prompt is not None
    assert question.question in provider.last_prompt
    assert "e1" in provider.last_prompt


def test_claim_evidence_validator_accepts_valid_references():
    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content="Some evidence.",
        ),
        Evidence(
            evidence_id="e2",
            source_id="source-1",
            question_id="q1",
            content="More evidence.",
        ),
    ]

    claims = [
        Claim(
            claim_id="c1",
            statement="A supported claim.",
            evidence_ids=["e1", "e2"],
            importance=4,
        )
    ]

    validated = ClaimEvidenceValidator.validate(
        claims=claims,
        evidence=evidence,
    )

    assert validated == claims


def test_claim_evidence_validator_rejects_unknown_reference():
    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content="Some evidence.",
        ),
    ]

    claims = [
        Claim(
            claim_id="c1",
            statement="A claim.",
            evidence_ids=["e999"],
            importance=3,
        )
    ]

    with pytest.raises(
        ValueError,
        match="unknown evidence IDs",
    ):
        ClaimEvidenceValidator.validate(
            claims=claims,
            evidence=evidence,
        )


@pytest.mark.asyncio
async def test_claim_verifier_creates_verification_result():
    response = """
    {
        "claim_id": "c1",
        "status": "supported",
        "confidence": 0.95,
        "evidence_ids": ["e1"],
        "explanation": "The evidence directly supports the claim."
    }
    """

    provider = FakeLLMProvider(response)
    verifier = ClaimVerifier(llm_provider=provider)

    claim = Claim(
        claim_id="c1",
        statement="Generative AI is increasingly used in software development.",
        evidence_ids=["e1"],
        importance=4,
    )

    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content=("Generative AI is increasingly used in software development."),
        ),
    ]

    result = await verifier.verify(
        claim=claim,
        evidence=evidence,
    )

    assert result.claim_id == "c1"
    assert result.status == "supported"
    assert result.confidence == 0.95
    assert result.evidence_ids == ["e1"]
    assert result.explanation == ("The evidence directly supports the claim.")
    assert provider.last_prompt is not None
    assert claim.statement in provider.last_prompt
    assert "e1" in provider.last_prompt


def test_verification_evidence_validator_accepts_valid_references():
    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content="Some evidence.",
        )
    ]

    result = VerificationResult(
        claim_id="c1",
        status="supported",
        confidence=0.9,
        evidence_ids=["e1"],
        explanation="Evidence supports the claim.",
    )

    validated = VerificationEvidenceValidator.validate(
        result=result,
        evidence=evidence,
    )

    assert validated == result


def test_verification_evidence_validator_rejects_unknown_reference():
    evidence = [
        Evidence(
            evidence_id="e1",
            source_id="source-1",
            question_id="q1",
            content="Some evidence.",
        )
    ]

    result = VerificationResult(
        claim_id="c1",
        status="supported",
        confidence=0.9,
        evidence_ids=["e999"],
        explanation="Evidence supports the claim.",
    )

    with pytest.raises(
        ValueError,
        match="unknown evidence IDs",
    ):
        VerificationEvidenceValidator.validate(
            result=result,
            evidence=evidence,
        )


@pytest.mark.asyncio
async def test_verifier_node_extracts_and_verifies_claims():
    claim_response = """
    [
        {
            "claim_id": "c1",
            "statement": "Generative AI is increasingly used in software development.",
            "evidence_ids": ["e1"],
            "importance": 4
        }
    ]
    """

    verification_response = """
    {
        "claim_id": "c1",
        "status": "supported",
        "confidence": 0.95,
        "evidence_ids": ["e1"],
        "explanation": "The evidence directly supports the claim."
    }
    """

    class SequentialFakeLLMProvider(LLMProvider):
        def __init__(self) -> None:
            self.responses = [
                claim_response,
                verification_response,
            ]

        async def generate(self, prompt: str) -> str:
            return self.responses.pop(0)

    provider = SequentialFakeLLMProvider()

    claim_extractor = ClaimExtractor(
        llm_provider=provider,
    )

    claim_verifier = ClaimVerifier(
        llm_provider=provider,
    )

    question = ResearchQuestion(
        id="q1",
        question="How is generative AI being adopted?",
        priority=3,
    )

    evidence = Evidence(
        evidence_id="e1",
        source_id="source-1",
        question_id="q1",
        content=("Generative AI is increasingly used in software development."),
    )

    research_state = ResearchState(
        request=ResearchRequest(query="How is generative AI being adopted?"),
        plan=ResearchPlan(
            objective="Understand generative AI adoption.",
            questions=[question],
        ),
        current_question_id="q1",
        evidences=[evidence],
    )

    state: ResearchGraphState = {
        "research_state": research_state,
    }

    result = await verifier_node(
        state=state,
        claim_extractor=claim_extractor,
        claim_verifier=claim_verifier,
    )

    updated_state = result["research_state"]

    assert len(updated_state.claims) == 1
    assert updated_state.claims[0].claim_id == "c1"

    assert len(updated_state.verification_results) == 1

    verification = updated_state.verification_results[0]

    assert verification.claim_id == "c1"
    assert verification.status == "supported"
    assert verification.confidence == 0.95
