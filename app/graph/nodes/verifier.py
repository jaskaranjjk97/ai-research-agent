import json

from app.graph.state import ResearchGraphState
from app.models.claim import Claim, VerificationResult
from app.models.evidence import Evidence
from app.models.research import ResearchQuestion
from app.providers.llm.base import LLMProvider


class ClaimExtractor:
    """Extract the Claims from the evidence with help of llm."""

    def __init__(
        self,
        llm_provider: LLMProvider,
    ) -> None:

        self.llm_provider = llm_provider

    async def extract_claims(
        self, evidence: list[Evidence], question: ResearchQuestion
    ) -> list[Claim]:
        """Extract claims supported by the provided evidence."""

        prompt = self._build_prompt(evidence=evidence, question=question)
        response = await self.llm_provider.generate(prompt)

        payload = json.loads(response)

        return [Claim.model_validate(item) for item in payload]

    @staticmethod
    def _build_prompt(
        evidence: list[Evidence],
        question: ResearchQuestion,
    ) -> str:
        """Build the claim extraction prompt."""

        evidence_text = "\n\n".join(
            (f"Evidence ID: {item.evidence_id}\nContent: {item.content}")
            for item in evidence
        )

        return f"""
Extract factual claims from the evidence below that help answer
the research question.

Research question:
{question.question}

Evidence:
{evidence_text}

Return a JSON array.

Each claim must contain:
- claim_id
- statement
- evidence_ids
- importance

Every evidence_id must refer to an evidence item provided above.

Do not include claims that cannot be supported by the provided evidence.
Do not include any information outside the JSON array.
""".strip()


class ClaimEvidenceValidator:
    """Validates that claims reference existing evidence."""

    @staticmethod
    def validate(
        claims: list[Claim],
        evidence: list[Evidence],
    ) -> list[Claim]:
        """Return claims whose evidence references are valid."""

        evidence_ids = {item.evidence_id for item in evidence}

        for claim in claims:
            missing_ids = [
                evidence_id
                for evidence_id in claim.evidence_ids
                if evidence_id not in evidence_ids
            ]

            if missing_ids:
                raise ValueError(
                    f"Claim '{claim.claim_id}' references "
                    f"unknown evidence IDs: {missing_ids}"
                )

        return claims


class ClaimVerifier:
    """Verifies whether evidence supports a claim."""

    def __init__(
        self,
        llm_provider: LLMProvider,
    ) -> None:
        self.llm_provider = llm_provider

    async def verify(
        self,
        claim: Claim,
        evidence: list[Evidence],
    ) -> VerificationResult:
        """Verify a claim against its referenced evidence."""

        evidence_by_id = {item.evidence_id: item for item in evidence}

        claim_evidence = [
            evidence_by_id[evidence_id]
            for evidence_id in claim.evidence_ids
            if evidence_id in evidence_by_id
        ]

        prompt = self._build_prompt(
            claim=claim,
            evidence=claim_evidence,
        )

        response = await self.llm_provider.generate(prompt)

        result = VerificationResult.model_validate_json(response)

        return VerificationEvidenceValidator.validate(
            result=result,
            evidence=evidence,
        )

    @staticmethod
    def _build_prompt(
        claim: Claim,
        evidence: list[Evidence],
    ) -> str:
        evidence_text = "\n\n".join(
            (f"Evidence ID: {item.evidence_id}\nContent: {item.content}")
            for item in evidence
        )

        return f"""
Verify the following factual claim using only the provided evidence.

Claim:
{claim.statement}

Evidence:
{evidence_text}

Return a JSON object containing:
- claim_id
- status
- confidence
- evidence_ids
- explanation

The status must be one of:
- supported
- partially_supported
- not_supported
- insufficient_evidence

The evidence_ids must contain only evidence IDs provided above.

Do not use outside knowledge.
Do not include any information outside the JSON object.
""".strip()


class VerificationEvidenceValidator:
    """Validates evidence references in verification results."""

    @staticmethod
    def validate(
        result: VerificationResult,
        evidence: list[Evidence],
    ) -> VerificationResult:
        """Validate that all referenced evidence actually exists."""

        evidence_ids = {item.evidence_id for item in evidence}

        missing_ids = [
            evidence_id
            for evidence_id in result.evidence_ids
            if evidence_id not in evidence_ids
        ]

        if missing_ids:
            raise ValueError(
                f"Verification result for claim '{result.claim_id}' "
                f"references unknown evidence IDs: {missing_ids}"
            )

        return result


async def verifier_node(
    state: ResearchGraphState,
    claim_extractor: ClaimExtractor,
    claim_verifier: ClaimVerifier,
) -> ResearchGraphState:
    """Extract and verify claim for the present research question."""

    research_state = state["research_state"]

    if research_state.plan is None:
        raise ValueError("Research plan is required before running verifier node.")

    if research_state.current_question_id is None:
        raise ValueError("Current question is required before running verifier node.")

    question = next(
        (
            item
            for item in research_state.plan.questions
            if item.id == research_state.current_question_id
        ),
        None,
    )

    if not question:
        raise ValueError("current research question could not be found in plan.")

    question_evidence = [
        item
        for item in research_state.evidences
        if item.question_id == research_state.current_question_id
    ]

    if not question_evidence:
        raise ValueError("No evidence found for the current question.")

    claims = await claim_extractor.extract_claims(
        evidence=question_evidence, question=question
    )

    ClaimEvidenceValidator.validate(
        claims=claims,
        evidence=question_evidence,
    )

    verification_results = []

    for claim in claims:
        result = await claim_verifier.verify(
            claim=claim,
            evidence=question_evidence,
        )

        verification_results.append(result)

    research_state.claims.extend(claims)
    research_state.verification_results.extend(verification_results)

    return state
