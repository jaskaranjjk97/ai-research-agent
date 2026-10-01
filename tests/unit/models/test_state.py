import pytest
from pydantic import ValidationError

from app.models.research import ResearchDepth, ResearchRequest
from app.models.state import ResearchState


def test_research_state_accepts_minimal_request():
    state = ResearchState(
        request=ResearchRequest(
            query="What is the current state of electric vehicle adoption?",
            depth=ResearchDepth.STANDARD,
        )
    )

    assert state.request.query == (
        "What is the current state of electric vehicle adoption?"
    )
    assert state.plan is None
    assert state.current_question_id is None
    assert state.search_results == []
    assert state.sources == []
    assert state.evidences == []
    assert state.claims == []
    assert state.verification_results == []
    assert state.research_gaps == []
    assert state.iterations == 0
    assert state.tool_calls == 0
    assert state.errors == []
    assert state.report is None


def test_research_state_accepts_custom_iteration_and_tool_calls():
    state = ResearchState(
        request=ResearchRequest(
            query="Research quantum computing.",
        ),
        iterations=2,
        tool_calls=7,
    )

    assert state.iterations == 2
    assert state.tool_calls == 7


def test_research_state_rejects_negative_iteration():
    with pytest.raises(ValidationError):
        ResearchState(
            request=ResearchRequest(
                query="Research quantum computing.",
            ),
            iterations=-1,
        )


def test_research_state_rejects_negative_tool_calls():
    with pytest.raises(ValidationError):
        ResearchState(
            request=ResearchRequest(
                query="Research quantum computing.",
            ),
            tool_calls=-1,
        )


def test_research_state_requires_request():
    with pytest.raises(ValidationError):
        ResearchState()
