import logging
import uuid

from fastapi import FastAPI, Request

from app.api.routes.research import router as research_router
from app.config.logging import configure_logging
from app.config.settings import get_settings

settings = get_settings()
configure_logging(settings)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API for an autonomous AI research agent.",
)


logger = logging.getLogger(__name__)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Attach a unique ID to each HTTP response and log request completion."""

    request_id = str(uuid.uuid4())

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "HTTP request completed",
        extra={"request_id": request_id},
    )

    return response


app.include_router(research_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return the application's basic health status."""

    return {"status": "ok"}
