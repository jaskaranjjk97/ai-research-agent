from pydantic import BaseModel, Field

from app.models.claim import Claim, VerificationResult
from app.models.evidence import Evidence
from app.models.report import ResearchReport
from app.models.research import ResearchPlan, ResearchRequest
from app.models.source import SearchResult, Source


class ResearchState(BaseModel):
    """Represents the complete state of research workflow."""

    request: ResearchRequest

    plan: ResearchPlan | None = None

    current_question_id: str | None = None

    search_results: list[SearchResult] = Field(
        default_factory=list,
        description="list of search results obtained during research.",
    )

    sources: list[Source] = Field(
        default_factory=list,
        description="list of sources selected and fetched for research.",
    )

    evidences: list[Evidence] = Field(
        default_factory=list,
        description="list of evidences extracted from research result.",
    )

    claims: list[Claim] = Field(
        default_factory=list,
        description="List of claims extracted.",
    )

    verification_results: list[VerificationResult] = Field(
        default_factory=list,
        description="list of Verification results.",
    )

    research_gaps: list[str] = Field(
        default_factory=list,
        description="Unsolved Questions or information gaps.",
    )

    iterations: int = Field(
        default=0,
        ge=0,
        description="Current research iteration.",
    )

    tool_calls: int = Field(
        default=0,
        ge=0,
        description="Number of tool calls made during research.",
    )

    errors: list[str] = Field(
        default_factory=list,
        description="List of errors encountered during research.",
    )

    report: ResearchReport | None = None
