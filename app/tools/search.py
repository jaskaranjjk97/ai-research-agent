from app.models.source import SearchResult
from app.providers.search.base import SearchProvider
from app.tools.execution import ToolExecutionController


class SearchTool:
    def __init__(
        self,
        provider: SearchProvider,
        max_results: int = 10,
        tool_execution_controller: ToolExecutionController | None = None,
    ) -> None:

        self.provider = provider
        self.max_results = max_results
        self.tool_execution_controller = tool_execution_controller

    async def search(
        self,
        query: str,
    ) -> list[SearchResult]:
        """Function that will search the web for us."""

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if self.tool_execution_controller:
            self.tool_execution_controller.check_and_record()

        return await self.provider.search(query=query, max_results=self.max_results)
