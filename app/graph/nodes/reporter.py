from app.graph.state import ResearchGraphState
from app.models.claim import Claim, VerificationResult, VerificationStatus
from app.models.evidence import Evidence
from app.models.report import ResearchReport
from app.models.research import ResearchPlan
from app.models.source import Source
from app.providers.llm.base import LLMProvider


class ReportGenerator:
    """Generates structured report based on verified claims."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    async def generate(
        self,
        plan: ResearchPlan,
        claims: list[Claim],
        verification_results: list[VerificationResult],
        evidence: list[Evidence],
        sources: list[Source],
    ) -> ResearchReport:
        usable_claims = self._select_usable_claims(
            claims=claims,
            verification_results=verification_results,
        )

        prompt = self._build_prompt(
            plan=plan,
            evidence=evidence,
            sources=sources,
            claims=usable_claims,
        )

        result = await self.llm_provider.generate(prompt)

        return ResearchReport.model_validate_json(result)

    @staticmethod
    def _select_usable_claims(
        claims: list[Claim],
        verification_results: list[VerificationResult],
    ) -> list[Claim]:
        verification_by_claim_id = {
            result.claim_id: result for result in verification_results
        }

        return [
            claim
            for claim in claims
            if verification_by_claim_id.get(claim.claim_id) is not None
            and verification_by_claim_id[claim.claim_id].status
            in {
                VerificationStatus.SUPPORTED,
                VerificationStatus.PARTIALLY_SUPPORTED,
            }
        ]

    @staticmethod
    def _build_prompt(
        plan: ResearchPlan,
        claims: list[Claim],
        evidence: list[Evidence],
        sources: list[Source],
    ) -> str:
        claims_text = "\n".join(
            (
                f"Claim ID: {claim.claim_id}\n"
                f"Statement: {claim.statement}\n"
                f"Evidence IDs: {', '.join(claim.evidence_ids)}"
            )
            for claim in claims
        )

        evidence_text = "\n".join(
            (
                f"Evidence ID: {item.evidence_id}\n"
                f"Source ID: {item.source_id}\n"
                f"Question ID: {item.question_id}\n"
                f"Content: {item.content}"
            )
            for item in evidence
            if any(item.evidence_id in claim.evidence_ids for claim in claims)
        )

        relevant_evidence_ids = {
            evidence_id for claim in claims for evidence_id in claim.evidence_ids
        }

        relevant_source_ids = {
            item.source_id
            for item in evidence
            if item.evidence_id in relevant_evidence_ids
        }

        sources_text = "\n".join(
            (f"Source ID: {source.source_id}\nTitle: {source.title}\nURL: {source.url}")
            for source in sources
            if source.source_id in relevant_source_ids
        )

        return f"""
Create a structured research report from the verified research findings.

Research objective:
{plan.objective}

Verified claims:
{claims_text}

Supporting evidence:
{evidence_text}

Sources:
{sources_text}

Return only a valid JSON object matching the ResearchReport schema.

The report must contain:
- title
- executive_summary
- sections
- citations

Each section must contain:
- section_id
- title
- content
- claim_ids

Each citation must contain:
- citation_id
- source_id
- claim_ids

Rules:
1. Only use the verified claims provided above.
2. Do not introduce unsupported factual claims.
3. Every claim_id must refer to a provided claim.
4. Every source_id must refer to a provided source.
5. Every citation must connect claims to their supporting sources.
6. Do not include information outside the provided research material.
7. Return JSON only.
""".strip()


async def reporter_node(
    state: ResearchGraphState,
    report_generator: ReportGenerator,
) -> ResearchGraphState:
    """Generate and store final research report."""

    research_state = state["research_state"]

    if not research_state.plan:
        raise ValueError("Research plan is required before running the reporter node.")

    report = await report_generator.generate(
        plan=research_state.plan,
        claims=research_state.claims,
        evidence=research_state.evidences,
        sources=research_state.sources,
        verification_results=research_state.verification_results,
    )

    research_state.report = report
    return state
