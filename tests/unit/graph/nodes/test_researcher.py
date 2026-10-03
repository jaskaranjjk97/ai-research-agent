import pytest

from app.graph.nodes.gap_checker import ResearchIterationGuard
from app.graph.nodes.researcher import Researcher, researcher_node, select_next_question
from app.graph.state import ResearchGraphState
from app.models.research import (
    ResearchPlan,
    ResearchQuestion,
    ResearchQuestionStatus,
    ResearchRequest,
)
from app.models.source import SearchResult
from app.models.state import ResearchState
from app.providers.search.base import SearchProvider
from app.tools.search import SearchTool


class FakeSearchProvider(SearchProvider):
    """Fake search provider for researcher tests."""

    def __init__(
        self,
        results: list[SearchResult],
    ) -> None:
        self.results = results
        self.last_query: str | None = None
        self.last_max_results: int | None = None

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        self.last_query = query
        self.last_max_results = max_results

        return self.results


def test_select_next_question_returns_highest_priority_pending_question():
    questions = [
        ResearchQuestion(
            id="q1",
            question="Question one",
            priority=2,
        ),
        ResearchQuestion(
            id="q2",
            question="Question two",
            priority=5,
        ),
        ResearchQuestion(
            id="q3",
            question="Question three",
            priority=3,
        ),
    ]

    result = select_next_question(questions)

    assert result is not None
    assert result.id == "q2"


def test_select_next_question_ignores_non_pending_questions():
    questions = [
        ResearchQuestion(
            id="q1",
            question="Question one",
            priority=5,
            status=ResearchQuestionStatus.ANSWERED,
        ),
        ResearchQuestion(
            id="q2",
            question="Question two",
            priority=2,
            status=ResearchQuestionStatus.PENDING,
        ),
    ]

    result = select_next_question(questions)

    assert result is not None
    assert result.id == "q2"


def test_select_next_question_returns_none_when_no_pending_questions():
    questions = [
        ResearchQuestion(
            id="q1",
            question="Question one",
            priority=5,
            status=ResearchQuestionStatus.ANSWERED,
        ),
    ]

    result = select_next_question(questions)

    assert result is None


@pytest.mark.asyncio
async def test_researcher_searches_for_question():
    results = [
        SearchResult(
            title="Generative AI Report",
            url="https://example.com/report",
            snippet="Research findings about generative AI.",
        ),
    ]

    provider = FakeSearchProvider(results)

    search_tool = SearchTool(
        provider=provider,
    )
    iteration_guard = ResearchIterationGuard(max_iterations=3)

    researcher = Researcher(
        search_tool=search_tool,
        iteration_guard=iteration_guard,
    )

    question = ResearchQuestion(
        id="q1",
        question="How is generative AI being adopted?",
        priority=3,
    )

    result = await researcher.research(question)

    assert result == results
    assert provider.last_query == "How is generative AI being adopted?"
    assert result[0].question_id == "q1"


@pytest.mark.asyncio
async def test_researcher_node_updates_graph_state():
    results = [
        SearchResult(
            title="AI Research",
            url="https://example.com/ai",
            snippet="Research information.",
        ),
    ]

    provider = FakeSearchProvider(results)

    search_tool = SearchTool(
        provider=provider,
    )

    iteration_guard = ResearchIterationGuard(max_iterations=3)

    researcher = Researcher(
        search_tool=search_tool,
        iteration_guard=iteration_guard,
    )

    request = ResearchRequest(
        query="Research generative AI adoption.",
    )

    plan = ResearchPlan(
        objective="Research generative AI adoption.",
        questions=[
            ResearchQuestion(
                id="q1",
                question="How is generative AI being adopted?",
                priority=5,
            ),
        ],
    )

    research_state = ResearchState(
        request=request,
        plan=plan,
    )

    graph_state: ResearchGraphState = {
        "research_state": research_state,
    }

    result = await researcher_node(
        state=graph_state,
        researcher=researcher,
    )

    assert result["research_state"].current_question_id == "q1"

    assert (
        result["research_state"].plan.questions[0].status
        == ResearchQuestionStatus.RESEARCHING
    )

    assert result["research_state"].search_results == results
