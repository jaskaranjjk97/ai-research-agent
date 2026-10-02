from app.models.source import Source
from app.providers.web.base import WebProvider
from app.tools.execution import ToolExecutionController


class WebFetchTool:
    """Tool for fetching web pages through a WebProvider."""

    def __init__(
        self,
        provider: WebProvider,
        tool_execution_controller: ToolExecutionController | None = None,
    ) -> None:
        self.provider = provider
        self.tool_execution_controller = tool_execution_controller

    async def fetch(
        self,
        url: str,
    ) -> Source:
        """Fetch and normalize a web page."""

        if not url.strip():
            raise ValueError("URL cannot be empty.")

        if self.tool_execution_controller:
            self.tool_execution_controller.check_and_record()

        return await self.provider.fetch(url)
