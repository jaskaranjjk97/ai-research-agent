from app.models.evidence import Evidence
from app.models.research import ResearchQuestion
from app.models.source import Source
from app.providers.extraction.base import ExtractionProvider
from app.tools.execution import ToolExecutionController


class ExtractionTool:
    """Extraction tool to extract evidence from sources based on research questions."""

    def __init__(
        self,
        provider: ExtractionProvider,
        tool_execution_controller: ToolExecutionController | None = None,
    ) -> None:
        self.provider = provider
        self.tool_execution_controller = tool_execution_controller

    async def extract(
        self, source: Source, question: ResearchQuestion
    ) -> list[Evidence]:
        """Extracts evidence from a source based on a research question."""

        if self.tool_execution_controller:
            self.tool_execution_controller.check_and_record()

        return await self.provider.extract(source=source, question=question)
