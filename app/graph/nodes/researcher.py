from app.graph.nodes.gap_checker import ResearchIterationGuard
from app.graph.state import ResearchGraphState
from app.models.research import ResearchQuestion, ResearchQuestionStatus
from app.models.source import SearchResult
from app.tools.search import SearchTool


def select_next_question(questions: list[ResearchQuestion]) -> ResearchQuestion:
    """This function will select the highest priority question for research."""

    pending_questions = [
        question
        for question in questions
        if question.status == ResearchQuestionStatus.PENDING
    ]

    if not pending_questions:
        return None

    return max(
        pending_questions,
        key=lambda question: question.priority,
    )


class Researcher:
    """Perform web research for a Resaerch question."""

    def __init__(
        self,
        search_tool: SearchTool,
        iteration_guard: ResearchIterationGuard,
    ) -> None:
        self.search_tool = search_tool
        self.iteration_guard = iteration_guard

    async def research(self, question: ResearchQuestion) -> list[SearchResult]:
        """Search the web for the question."""

        results = await self.search_tool.search(question.question)

        for result in results:
            result.question_id = question.id

        return results


async def researcher_node(
    state: ResearchGraphState, researcher: Researcher
) -> ResearchGraphState:
    """accept the state,research the question and update the state."""

    research_state = state["research_state"]

    if research_state.plan is None:
        raise ValueError("Research plan is required befor running the research node.")

    question = select_next_question(
        questions=research_state.plan.questions,
    )

    if question is None:
        raise ValueError("No pending research question is available.")

    researcher.iteration_guard.start_iteration(research_state)

    question.status = ResearchQuestionStatus.RESEARCHING
    research_state.current_question_id = question.id

    results = await researcher.research(question)

    research_state.search_results.extend(results)
    # because agent may perform many research iterations
    # so avoid research_state.search_results=results

    return state
