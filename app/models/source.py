from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class SearchResult(BaseModel):
    """Represents a single search result from a search engine."""

    title: str = Field(
        min_length=1,
        max_length=1000,
        description="The title of the search result.",
    )

    url: HttpUrl

    snippet: str = Field(
        default="",
        max_length=5000,
        description="A brief snippet or summary of the search result.",
    )

    source_name: str | None = Field(
        default=None,
        max_length=500,
        description="The source or domain of the search result.",
    )


class Source(BaseModel):
    """Represents the source selected for reaserach."""

    source_id: str = Field(
        min_length=1,
        description="Unique id representing the source.",
    )

    title: str = Field(
        min_length=1,
        max_length=1000,
        description="The title of the source.",
    )

    url: HttpUrl

    domain: str = Field(
        min_length=1,
        max_length=500,
    )

    content: str = Field(
        min_length=1,
        description="The content of the source",
    )

    source_type: str = Field(
        default="other",
        min_length=1,
        max_length=100,
    )

    published_at: datetime | None = None

    retrieved_at: datetime
