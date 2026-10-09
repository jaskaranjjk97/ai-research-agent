from functools import lru_cache

from app.config.settings import get_settings
from app.dependencies import build_configured_research_service
from app.services.research_service import ResearchService


@lru_cache(maxsize=1)
def get_research_service_dependency() -> ResearchService:
    """Build and cache the configured research service."""

    settings = get_settings()
    return build_configured_research_service(settings)
