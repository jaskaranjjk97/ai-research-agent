from enum import StrEnum

from pydantic import BaseModel, Field


class ResearchDepth(StrEnum):
    """Controls how extensively the agent performs research."""

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class ResearchQuestionStatus(StrEnum):
    """Tells about the status of a research question."""

    PENDING = "pending"
    RESEARCHING = "researching"
    ANSWERED = "answered"
    INSUFFICIENT = "insufficient"


class ResearchRequest(BaseModel):
    """Represents a user's research request."""

    query: str = Field(
        min_length=3,
        max_length=5000,
        description="The research question or objective.",
    )

    depth: ResearchDepth = Field(
        default=ResearchDepth.STANDARD,
        description="The desired research depth.",
    )


class ResearchQuestion(BaseModel):
    """Represents a one question to researched."""

    id: str = Field(
        min_length=1,
        description="The unique identifier for the research question.",
    )

    question: str = Field(
        min_length=3,
        max_length=2000,
        description="The specific question to research.",
    )

    priority: int = Field(
        default=1,
        ge=1,
        le=5,
        description="The priority of the research question (1-5).",
    )

    status: ResearchQuestionStatus = Field(
        default=ResearchQuestionStatus.PENDING,
        description="The current status of the research question.",
    )


class ResearchPlan(BaseModel):
    """Represents a research plan consisting of multiple research questions."""

    objective: str = Field(
        min_length=1,
        max_length=5000,
        description="The main objective or goal of the research plan.",
    )

    questions: list[ResearchQuestion] = Field(
        default_factory=list,
        min_length=1,
        description="A list of research questions to be addressed in the plan.",
    )
