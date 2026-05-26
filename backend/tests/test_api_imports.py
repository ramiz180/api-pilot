"""API-level tests for the import endpoints.

POST /api/imports/upload  — multipart file upload
POST /api/imports/url     — JSON body with URL

These tests use a real PostgreSQL database and the FastAPI ASGI test client.
DB state is cleaned up after each test by the ``db`` fixture from conftest.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Test 1 — successful file upload
# ---------------------------------------------------------------------------


async def test_upload_petstore_v3_returns_201_with_suite(
    client: AsyncClient,
    db: AsyncSession,
) -> None:
    """Uploading a valid Swagger spec creates a suite and returns 201."""
    content = (FIXTURES / "petstore_v3.json").read_bytes()

    response = await client.post(
        "/api/imports/upload",
        files={"file": ("petstore_v3.json", content, "application/json")},
    )

    assert response.status_code == 201, response.text

    data = response.json()
    assert "id" in data
    assert data["name"] == "Swagger Petstore - OpenAPI 3.0"
    assert data["generation_status"] == "parsed"
    assert isinstance(data["endpoints"], list)
    assert len(data["endpoints"]) == 19

    # Verify each endpoint has the expected summary fields only
    ep = data["endpoints"][0]
    assert "id" in ep
    assert "method" in ep
    assert "path" in ep
    assert "name" in ep
    assert "schema" not in ep  # EndpointDetailOut is deferred to Sprint 1d


# ---------------------------------------------------------------------------
# Test 2 — empty file → 400
# ---------------------------------------------------------------------------


async def test_upload_empty_file_returns_400(client: AsyncClient) -> None:
    """An empty file upload must be rejected with 400 before hitting the service."""
    response = await client.post(
        "/api/imports/upload",
        files={"file": ("empty.json", b"", "application/json")},
    )
    assert response.status_code == 400, response.text


# ---------------------------------------------------------------------------
# Test 3 — invalid spec → 422
# ---------------------------------------------------------------------------


async def test_upload_invalid_swagger_returns_422(
    client: AsyncClient,
    db: AsyncSession,
) -> None:
    """Content that is not a Swagger spec returns 422 with a detail message."""
    response = await client.post(
        "/api/imports/upload",
        files={"file": ("bad.json", b"not a swagger spec", "application/json")},
    )
    assert response.status_code == 422, response.text
    body = response.json()
    assert "detail" in body
    # The detail should mention parsing (not an internal server error message)
    assert len(body["detail"]) > 0


# ---------------------------------------------------------------------------
# Test 4 — URL import (monkeypatched fetcher)
# ---------------------------------------------------------------------------


async def test_import_from_url_works_with_mock(
    client: AsyncClient,
    db: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """URL import delegates to the fetcher; mocking it exercises the happy path."""
    petstore_bytes = (FIXTURES / "petstore_v3.json").read_bytes()

    async def _mock_fetch(url: str, timeout: float = 30.0) -> tuple[bytes, str]:
        return petstore_bytes, "openapi.json"

    monkeypatch.setattr(
        "app.services.import_service.fetch_spec_from_url", _mock_fetch
    )

    response = await client.post(
        "/api/imports/url",
        json={"url": "https://example.com/openapi.json"},
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert isinstance(data["endpoints"], list)
    assert len(data["endpoints"]) > 0


# ---------------------------------------------------------------------------
# Test 5 — invalid URL body → 422 (Pydantic validation)
# ---------------------------------------------------------------------------


async def test_import_from_url_invalid_url_returns_422(
    client: AsyncClient,
) -> None:
    """A non-URL string in the request body must fail Pydantic validation (422)."""
    response = await client.post(
        "/api/imports/url",
        json={"url": "not-a-url"},
    )
    assert response.status_code == 422, response.text
