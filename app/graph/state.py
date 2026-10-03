from typing import TypedDict

from app.models.state import ResearchState


class ResearchGraphState(TypedDict):
    """State passed between nodes in the research graph."""

    research_state: ResearchState
