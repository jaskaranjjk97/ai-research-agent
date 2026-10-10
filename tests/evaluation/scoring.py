from dataclasses import asdict, dataclass

from app.models.claim import Claim
from app.models.report import ResearchReport
from app.models.source import Source
from app.verification.citation_validator import CitationValidator


@dataclass(frozen=True)
class EvaluationScore:
    """Contains deterministic structural evaluation metrics."""

    citation_integrity: float
    claim_citation_coverage: float | None
    section_coverage: float

    def to_dict(self) -> dict[str, float | None]:
        """Return scores as a dictionary."""
        return asdict(self)


def evaluate_report(
    report: ResearchReport,
    claims: list[Claim],
    sources: list[Source],
    expected_sections: list[str],
) -> EvaluationScore:
    """Evaluate citation integrity, claim coverage, and section coverage."""

    CitationValidator.validate(
        report=report,
        claims=claims,
        sources=sources,
    )

    citation_integrity = 1.0

    cited_claim_ids = {
        claim_id for citation in report.citations for claim_id in citation.claim_ids
    }

    if claims:
        claim_citation_coverage = sum(
            claim.claim_id in cited_claim_ids for claim in claims
        ) / len(claims)
    else:
        claim_citation_coverage = None

    actual_section_titles = {
        section.title.strip().casefold() for section in report.sections
    }

    normalized_expected_sections = {
        title.strip().casefold() for title in expected_sections if title.strip()
    }

    if normalized_expected_sections:
        section_coverage = len(
            actual_section_titles & normalized_expected_sections
        ) / len(normalized_expected_sections)
    else:
        section_coverage = 1.0

    return EvaluationScore(
        citation_integrity=citation_integrity,
        claim_citation_coverage=claim_citation_coverage,
        section_coverage=section_coverage,
    )
