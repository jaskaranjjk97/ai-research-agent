import pytest

from app.graph.nodes.planner import Planner, planner_node
from app.graph.state import ResearchGraphState
from app.models.research import (
    ResearchDepth,
    ResearchQuestionStatus,
    ResearchRequest,
)
from app.models.state import ResearchState
from app.providers.llm.base import LLMProvider


class FakeLLMProvider(LLMProvider):
    """Fake LLM provider for planner tests."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.last_prompt: str | None = None

    async def generate(
        self,
        prompt: str,
    ) -> str:
        self.last_prompt = prompt
        return self.response


@pytest.mark.asyncio
async def test_planner_creates_research_plan():
    response = """
    {
        "objective": "Research the impact of generative AI on software development.",
        "questions": [
            {
                "id": "q1",
                "question": 
                "How is generative AI being adopted in software development?"
                ,
                "priority": 1,
                "status": "pending"
            },
            {
                "id": "q2",
                "question": 
                "How is generative AI being adopted in software development?"
                ,
                "priority": 2,
                "status": "pending"
            }
        ]
    }
    """

    provider = FakeLLMProvider(response)

    planner = Planner(
        llm_provider=provider,
    )

    request = ResearchRequest(
        query="What is the impact of generative AI on software development?",
        depth=ResearchDepth.STANDARD,
    )

    plan = await planner.create_plan(request)

    assert plan.objective == (
        "Research the impact of generative AI on software development."
    )

    assert len(plan.questions) == 2
    assert plan.questions[0].id == "q1"
    assert plan.questions[0].status == ResearchQuestionStatus.PENDING
    assert plan.questions[1].priority == 2

    assert provider.last_prompt is not None
    assert request.query in provider.last_prompt


@pytest.mark.asyncio
async def test_planner_rejects_invalid_plan():
    response = """
    {
        "objective": "Research AI",
        "questions": []
    }
    """

    provider = FakeLLMProvider(response)

    planner = Planner(
        llm_provider=provider,
    )

    request = ResearchRequest(
        query="Research AI",
    )

    with pytest.raises(ValueError):
        await planner.create_plan(request)


@pytest.mark.asyncio
async def test_planner_node_stores_plan_in_graph_state():
    response = """
    {
        "objective": "Research the impact of generative AI.",
        "questions": [
            {
                "id": "q1",
                "question": "How is generative AI being adopted?",
                "priority": 1,
                "status": "pending"
            }
        ]
    }
    """

    provider = FakeLLMProvider(response)

    planner = Planner(
        llm_provider=provider,
    )

    request = ResearchRequest(
        query="Research the impact of generative AI.",
    )

    research_state = ResearchState(
        request=request,
    )

    graph_state: ResearchGraphState = {
        "research_state": research_state,
    }

    result = await planner_node(
        state=graph_state,
        planner=planner,
    )

    assert result["research_state"].plan is not None

    assert (
        result["research_state"].plan.objective
        == "Research the impact of generative AI."
    )

    assert len(result["research_state"].plan.questions) == 1
