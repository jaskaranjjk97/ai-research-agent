from app.graph.state import ResearchGraphState
from app.models.research import ResearchPlan, ResearchRequest
from app.providers.llm.base import LLMProvider


class Planner:
    """Creates a structured research plan from a research request."""

    def __init__(
        self,
        llm_provider: LLMProvider,
    ) -> None:
        self.llm_provider = llm_provider

    async def create_plan(
        self,
        request: ResearchRequest,
    ) -> ResearchPlan:
        """Create and validate a research plan."""

        prompt = self._build_prompt(request)

        response = await self.llm_provider.generate(prompt)

        return ResearchPlan.model_validate_json(response)

    @staticmethod
    def _build_prompt(
        request: ResearchRequest,
    ) -> str:
        """Build the planning prompt."""

        return f"""
Create a structured research plan for the following research request.

Research request:
{request.query}

Return a JSON object containing:
- objective
- questions

Each question must contain:
- id
- question
- priority
- status

The status for every new question must be "pending".

Do not include any information outside the JSON object.
""".strip()


async def planner_node(
    state: ResearchGraphState, planner: Planner
) -> ResearchGraphState:
    """Create the research plan and store it in Planner Node."""

    research_state = state["research_state"]

    plan = await planner.create_plan(research_state.request)

    research_state.plan = plan
    # updating the research_state with the plan created above

    return state
