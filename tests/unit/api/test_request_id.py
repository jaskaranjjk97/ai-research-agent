import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_request_id_is_returned_in_response():
    response = TestClient(app).get("/health")

    assert response.status_code == 200

    request_id = response.headers["X-Request-ID"]
    assert uuid.UUID(request_id)


def test_each_request_gets_a_unique_id():
    client = TestClient(app)

    first_response = client.get("/health")
    second_response = client.get("/health")

    assert (
        first_response.headers["X-Request-ID"]
        != second_response.headers["X-Request-ID"]
    )
