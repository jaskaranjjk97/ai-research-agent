from app.models.source import SearchResult, Source
from app.tools.web_fetch import WebFetchTool


class SourceService:
    """Converts SearchResult data into Source structured data."""

    def __init__(self, web_fetch_tool: WebFetchTool) -> None:
        self.web_fetch_tool = web_fetch_tool

    async def fetch_source(self, search_result: SearchResult) -> Source:
        """Fetch a complete source from Search result."""

        return await self.web_fetch_tool.fetch(str(search_result.url))
