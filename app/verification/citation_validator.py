from app.models.claim import Claim
from app.models.report import Citation, ResearchReport
from app.models.source import Source


class CitationValidator:
    """Validates the citations referenced in the research report."""

    @staticmethod
    def validate(
        report: ResearchReport,
        claims: list[Claim],
        sources: list[Source],
    ) -> ResearchReport:

        claim_ids = {claim.claim_id for claim in claims}
        source_ids = {source.source_id for source in sources}

        for citation in report.citations:
            CitationValidator._validate_citation(
                citation=citation,
                source_ids=source_ids,
                claim_ids=claim_ids,
            )

        return report

    @staticmethod
    def _validate_citation(
        citation: Citation,
        source_ids: set[str],
        claim_ids: set[str],
    ) -> None:

        if citation.source_id not in source_ids:
            raise ValueError(
                f"Citation '{citation.citation_id}' references "
                f"unknown source ID: {citation.source_id}"
            )

        missing_claim_ids = [
            claim_id for claim_id in citation.claim_ids if claim_id not in claim_ids
        ]

        if missing_claim_ids:
            raise ValueError(
                f"Citation '{citation.citation_id}' references "
                f"unknown claim IDs: {missing_claim_ids}"
            )
