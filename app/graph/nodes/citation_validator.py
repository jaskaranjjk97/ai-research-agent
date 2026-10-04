from app.graph.state import ResearchGraphState
from app.verification.citation_validator import CitationValidator


async def citation_validation_node(
    state: ResearchGraphState,
    citation_validator: CitationValidator,
) -> ResearchGraphState:
    """Validate citations in the generated research report."""

    research_state = state["research_state"]

    if research_state.report is None:
        raise ValueError("Research report is required before citation validation.")

    citation_validator.validate(
        report=research_state.report,
        claims=research_state.claims,
        sources=research_state.sources,
    )

    return state
