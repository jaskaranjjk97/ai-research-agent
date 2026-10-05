from app.models.report import ResearchReport
from app.models.research import ResearchRequest
from app.services.research_service import ResearchService


class FakeResearchAgent:
    """Fake research agent used for service tests."""

    def __init__(self, report: ResearchReport) -> None:
        self.report = report
        self.received_request = None

    async def run(self, request: ResearchRequest) -> ResearchReport:
        self.received_request = request
        return self.report


def create_report() -> ResearchReport:
    return ResearchReport(
        title="Test Research Report",
        executive_summary="This is a test report.",
        sections=[
            {
                "section_id": "section-1",
                "title": "Introduction",
                "content": "Test content.",
                "claim_ids": [],
            }
        ],
        citations=[],
    )


async def test_service_returns_report():
    report = create_report()
    agent = FakeResearchAgent(report)
    service = ResearchService(agent)

    request = ResearchRequest(
        query="Test research request",
    )

    result = await service.run(request)

    assert result == report


async def test_service_passes_request_to_agent():
    report = create_report()
    agent = FakeResearchAgent(report)
    service = ResearchService(agent)

    request = ResearchRequest(
        query="Test research request",
    )

    await service.run(request)

    assert agent.received_request == request
