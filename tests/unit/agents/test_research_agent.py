from app.agents.research_agent import ResearchAgent
from app.models.report import ResearchReport
from app.models.research import ResearchRequest
from app.models.state import ResearchState


class FakeGraph:
    """Fake compiled graph used for testing the research agent."""

    def __init__(self, report: ResearchReport | None) -> None:
        self.report = report
        self.received_state = None

    async def ainvoke(self, state):
        self.received_state = state

        research_state = state["research_state"]
        research_state.report = self.report

        return {
            "research_state": research_state,
        }


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


async def test_agent_returns_report():
    report = create_report()
    graph = FakeGraph(report)
    agent = ResearchAgent(graph)

    request = ResearchRequest(
        query="Test research request",
    )

    result = await agent.run(request)

    assert result == report


async def test_agent_passes_request_to_graph():
    report = create_report()
    graph = FakeGraph(report)
    agent = ResearchAgent(graph)

    request = ResearchRequest(
        query="Test research request",
    )

    await agent.run(request)

    received_state = graph.received_state

    assert received_state is not None

    research_state: ResearchState = received_state["research_state"]

    assert research_state.request == request


async def test_agent_raises_when_report_is_missing():
    graph = FakeGraph(report=None)
    agent = ResearchAgent(graph)

    request = ResearchRequest(
        query="Test research request",
    )

    try:
        await agent.run(request)
    except RuntimeError as exc:
        assert str(exc) == ("Research graph completed without producing a report.")
    else:
        raise AssertionError("Expected RuntimeError was not raised.")
