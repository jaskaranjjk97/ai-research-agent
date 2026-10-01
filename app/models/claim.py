from enum import StrEnum

from pydantic import BaseModel, Field


class VerificationStatus(StrEnum):
    """Tells About the Verification status of the claim."""

    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    NOT_SUPPORTED = "not_supported"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class Claim(BaseModel):
    """Represents a Factual Claim that may appear in Research report."""

    claim_id: str = Field(
        min_length=1,
        max_length=100,
        description="Unique id representing the claim.",
    )

    evidence_ids: list[str] = Field(
        min_length=1,
        max_length=100,
        description="Unique id representing the evidence supporting the claim.",
    )

    statement: str = Field(
        min_length=1,
        max_length=5000,
        description="The factual statement being evaluated.",
    )

    importance: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Importance of the claim on a scale of 1 to 5.",
    )


class VerificationResult(BaseModel):
    """Represents the result of verifying a claim."""

    claim_id: str = Field(
        min_length=1,
        max_length=100,
        description="Unique id representing the claim.",
    )

    status: VerificationStatus = Field(
        description="The verification status of the claim."
    )

    evidence_ids: list[str] = Field(
        min_length=1,
        description="Evidence which was considered during the verification process.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 to 1.0",
    )

    explanation: str = Field(
        min_length=1,
        max_length=5000,
        description="Explanation why evidence supports or fails to support the claim.",
    )
