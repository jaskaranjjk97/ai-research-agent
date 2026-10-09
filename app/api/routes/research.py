from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_research_service_dependency
from app.models.report import ResearchReport
from app.models.research import ResearchRequest
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
) -> ResearchReport:
    """Execute a research request and return the generated report."""

    try:
        return await service.run(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research execution failed.",
        ) from exc
