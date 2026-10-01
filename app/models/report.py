from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Represents the citation for the source of research."""

    citation_id: str = Field(
        min_length=1,
        description="Unique citation identifier used in the report.",
    )

    source_id: str = Field(
        min_length=1,
        description="Identifier for the source being cited.",
    )

    claim_ids: list[str] = Field(
        min_length=1,
        description="identifier for the claim being made.",
    )


class ReportSection(BaseModel):
    """Represents one section of the final report."""

    section_id: str = Field(
        min_length=1,
        description="Unique identifier for the report section.",
    )

    title: str = Field(
        min_length=1,
        max_length=500,
        description="Title of the report section.",
    )

    content: str = Field(
        min_length=1,
        max_length=20000,
        description="Content of the report section.",
    )

    claim_ids: list[str] = Field(
        default_factory=list,
        description="list of claims associated with this section.",
    )


class ResearchReport(BaseModel):
    """Represents the final structured report of the agent."""

    title: str = Field(
        min_length=1,
        max_length=500,
        description="Title of the research report.",
    )

    executive_summary: str = Field(
        min_length=1,
        max_length=10000,
        description="Executive summary of the research report.",
    )

    sections: list[ReportSection] = Field(
        default_factory=list,
        min_length=1,
        description="List of sections in the research report.",
    )

    citations: list[Citation] = Field(
        default_factory=list,
        description="citation sources cited in the report.",
    )
