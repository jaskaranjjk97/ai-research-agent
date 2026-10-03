from app.graph.state import ResearchGraphState
from app.models.research import ResearchRequest
from app.models.state import ResearchState


def test_research_graph_state_contains_research_state():
    request = ResearchRequest(
        query="What are the major developments in generative AI?",
    )

    research_state = ResearchState(
        request=request,
    )

    graph_state: ResearchGraphState = {
        "research_state": research_state,
    }

    assert graph_state["research_state"] == research_state
