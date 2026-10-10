import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_research_service_dependency
from app.config.settings import Settings, get_settings
from app.models.report import ResearchReport
from app.models.research import ResearchRequest
from app.providers.errors import ProviderError
from app.services.research_service import ResearchService

router = APIRouter(prefix="/api/v1", tags=["research"])


@router.post(
    "/research",
    response_model=ResearchReport,
    status_code=status.HTTP_200_OK,
)
async def run_research(
    request: ResearchRequest,
    service: Annotated[
        ResearchService,
        Depends(get_research_service_dependency),
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ResearchReport:
    """Execute a research request and return the generated report."""

    try:
        async with asyncio.timeout(settings.research_request_timeout_seconds):
            return await service.run(request)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Research execution timed out.",
        ) from exc
    except ProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="An upstream provider request failed.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research execution failed.",
        ) from exc
