from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Represents the specific evidence taken from source."""

    evidence_id: str = Field(
        min_length=1,
        max_length=50,
        description="Unique id for each Evidence.",
    )

    source_id: str = Field(
        min_length=1,
        max_length=100,
        description="Unique id of source.",
    )

    question_id: str = Field(
        min_length=1,
    )

    content: str = Field(
        min_length=1,
        max_length=10000,
    )

    location: str | None = Field(
        default=None,
        max_length=1000,
        description="The location of evidence within the source.",
    )
