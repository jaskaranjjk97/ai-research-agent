from app.agents.research_agent import ResearchAgent
from app.models.report import ResearchReport
from app.models.research import ResearchRequest


class ResearchService:
    """Application service for executing research requests."""

    def __init__(self, research_agent: ResearchAgent) -> None:
        self.research_agent = research_agent

    async def run(self, request: ResearchRequest) -> ResearchReport:
        """Execute the research request and return final report."""

        return await self.research_agent.run(request)
