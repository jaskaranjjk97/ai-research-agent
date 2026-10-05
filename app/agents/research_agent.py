from typing import Any

from app.graph.state import ResearchGraphState
from app.models.report import ResearchReport
from app.models.research import ResearchRequest
from app.models.state import ResearchState


class ResearchAgent:
    """Executes the compiled research graph."""

    def __init__(self, graph: Any) -> None:
        self.graph = graph

    async def run(self, request: ResearchRequest) -> ResearchReport:
        research_state = ResearchState(request=request)

        initial_state: ResearchGraphState = {"research_state": research_state}

        final_state = await self.graph.ainvoke(initial_state)
        # graph.ainvoke() instead of graph.invoke() as our graph nodes
        # are asynchronous.

        final_research_state = final_state["research_state"]

        if final_research_state.report is None:
            raise RuntimeError("Research graph completed without producing a report.")

        return final_research_state.report
