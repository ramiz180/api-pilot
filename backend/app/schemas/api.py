"""Public API contract schemas.

These models form the HTTP-level contract between the frontend and the backend.
They are deliberately separate from the internal parser models in
``app.parsers.models`` — callers must not be coupled to internal
implementation details.

Naming conventions
------------------
*In   — request bodies accepted by POST/PUT endpoints
*Out  — response bodies returned to callers
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------


class ImportFromUrlIn(BaseModel):
    """Request body for POST /api/imports/url."""

    url: HttpUrl


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


class EndpointOut(BaseModel):
    """Endpoint summary — included inside SuiteDetailOut.

    The full ``schema`` JSONB blob is intentionally omitted here; it will be
    surfaced via GET /api/endpoints/{id} (Sprint 1d) when the frontend
    needs schema-heavy views.
    """

    id: UUID
    method: str
    path: str
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class EndpointDetailOut(EndpointOut):
    """Full endpoint detail — includes the parsed schema blob.

    Used by GET /api/endpoints/{id} (Sprint 1d).
    ``validation_alias`` maps the ORM attribute ``endpoint_schema`` to the
    Python field ``schema_`` which is serialised as ``"schema"`` in JSON.
    """

    schema_: dict = Field(
        alias="schema",
        validation_alias="endpoint_schema",  # ORM Python attribute name
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# ---------------------------------------------------------------------------
# Suites
# ---------------------------------------------------------------------------


class SuiteSummaryOut(BaseModel):
    """Suite list-view item — no endpoint list, includes a count instead."""

    id: UUID
    name: str
    spec_id: UUID
    generation_status: str
    endpoint_count: int         # dynamically set by suite_service.list_suites
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SuiteDetailOut(BaseModel):
    """Suite detail view — includes endpoint summaries (no full schema)."""

    id: UUID
    name: str
    spec_id: UUID
    generation_status: str
    endpoints: list[EndpointOut]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
