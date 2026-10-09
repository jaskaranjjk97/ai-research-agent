from fastapi import FastAPI

from app.api.routes.research import router as research_router
from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API for an autonomous AI research agent.",
)

app.include_router(research_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return the application's basic health status."""

    return {"status": "ok"}
