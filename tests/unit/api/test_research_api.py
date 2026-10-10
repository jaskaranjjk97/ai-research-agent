import asyncio

from fastapi.testclient import TestClient

from app.api.dependencies import get_research_service_dependency
from app.config.settings import Settings, get_settings
from app.main import app
from app.models.report import ResearchReport
from app.providers.errors import ProviderError


class FakeResearchService:
    async def run(self, request):
        return ResearchReport(
            title="Test Report",
            executive_summary="Test summary.",
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


def test_health_check():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_research_endpoint_returns_report():
    app.dependency_overrides[get_research_service_dependency] = lambda: (
        FakeResearchService()
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/research",
            json={"query": "Research Python async programming"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Test Report"
        assert response.json()["executive_summary"] == "Test summary."
    finally:
        app.dependency_overrides.clear()


def test_research_endpoint_rejects_invalid_request():
    app.dependency_overrides[get_research_service_dependency] = lambda: (
        FakeResearchService()
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/research",
            json={"query": "Hi"},
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_research_endpoint_handles_service_failure():
    class FailingResearchService:
        async def run(self, request):
            raise RuntimeError("Internal provider details")

    app.dependency_overrides[get_research_service_dependency] = lambda: (
        FailingResearchService()
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/research",
            json={"query": "Research Python async programming"},
        )

        assert response.status_code == 500
        assert response.json() == {"detail": "Research execution failed."}
        assert "Internal provider details" not in response.text
    finally:
        app.dependency_overrides.clear()


def test_research_endpoint_returns_504_on_timeout():
    class SlowResearchService:
        async def run(self, request):
            await asyncio.sleep(0.1)

    app.dependency_overrides[get_research_service_dependency] = lambda: (
        SlowResearchService()
    )
    app.dependency_overrides[get_settings] = lambda: Settings(
        research_request_timeout_seconds=0.01
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/research",
            json={"query": "Research Python async programming"},
        )

        assert response.status_code == 504
        assert response.json() == {"detail": "Research execution timed out."}
    finally:
        app.dependency_overrides.clear()


def test_research_endpoint_handles_provider_failure():
    class FailingResearchService:
        async def run(self, request):
            raise ProviderError("Provider failed")

    app.dependency_overrides[get_research_service_dependency] = lambda: (
        FailingResearchService()
    )

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/research",
            json={"query": "Research Python async programming"},
        )

        assert response.status_code == 502
    finally:
        app.dependency_overrides.clear()
