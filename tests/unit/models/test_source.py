from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.source import SearchResult, Source


def test_search_result_accepts_valid_url():
    result = SearchResult(
        title="EV Market Report",
        url="https://example.com/report",
        snippet="India EV market information.",
    )

    assert str(result.url) == "https://example.com/report"


def test_search_result_rejects_invalid_url():
    with pytest.raises(ValidationError):
        SearchResult(
            title="EV Market Report",
            url="not-a-valid-url",
        )


def test_search_result_source_name_is_optional():
    result = SearchResult(
        title="EV Market Report",
        url="https://example.com/report",
    )

    assert result.source_name is None


def test_source_accepts_valid_data():
    retrieved_at = datetime.now(UTC)

    source = Source(
        source_id="src-001",
        title="EV Market Report",
        url="https://example.com/report",
        domain="example.com",
        content="India's EV market information.",
        retrieved_at=retrieved_at,
    )

    assert source.source_id == "src-001"
    assert source.domain == "example.com"
    assert source.retrieved_at == retrieved_at


def test_source_published_at_is_optional():
    source = Source(
        source_id="src-001",
        title="EV Market Report",
        url="https://example.com/report",
        domain="example.com",
        content="India's EV market information.",
        retrieved_at=datetime.now(UTC),
    )

    assert source.published_at is None
