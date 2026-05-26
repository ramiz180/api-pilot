"""Spec import service — ties storage + parser + DB into one transaction.

Public functions
----------------
import_from_upload(db, workspace_id, content, filename) -> Suite
    Import a spec from uploaded file bytes.

import_from_url(db, workspace_id, url) -> Suite
    Fetch a spec from a URL then import it.

Both functions commit the transaction themselves and return the created
Suite with its endpoints relationship already loaded.  They do NOT create
their own session — the caller passes an AsyncSession in.

Error handling
--------------
On any failure the service raises SpecImportError.  The DB transaction is
left uncommitted; the caller (or the session context manager) must rollback.

Storage-file lifecycle
----------------------
The raw spec bytes are written to storage *before* the DB commit.  If the
DB commit never happens (parsing failed, DB error) the file becomes orphaned.
TODO V1.5: add a periodic orphaned-file cleanup job.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.endpoint import Endpoint
from app.models.spec import Spec
from app.models.suite import Suite
from app.models.workspace import Workspace
from app.parsers.enums import SpecSource
from app.parsers.errors import ParserError
from app.parsers.fetcher import fetch_spec_from_url
from app.parsers.swagger_parser import parse_swagger
from app.services import SpecImportError
from app.storage.factory import get_storage

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _storage_ext(filename: str) -> str:
    """Return a normalised file extension for use in a storage key."""
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext if ext in ("json", "yaml", "yml") else "json"


# ---------------------------------------------------------------------------
# Core import logic
# ---------------------------------------------------------------------------


async def _import_spec(
    db: AsyncSession,
    workspace_id: UUID,
    content: bytes,
    filename: str,
    source_url: str | None,
) -> Suite:
    """Import *content* as a Swagger/OpenAPI spec.

    Steps
    -----
    1. Validate workspace exists.
    2. Generate a storage key and write the raw bytes.
    3. Create a Spec row (flush, don't commit).
    4. Parse the content with the Swagger parser.
    5. Update spec.parsed_at; create Suite + Endpoint rows.
    6. Commit the transaction.
    7. Return the Suite with endpoints loaded.

    Args:
        db:           Caller-owned AsyncSession (this function commits it).
        workspace_id: UUID of the target workspace.
        content:      Raw file bytes.
        filename:     Original filename (used for extension + parse hint).
        source_url:   Non-None when importing from a URL (stored on the Spec
                      row instead of original_filename).

    Raises:
        SpecImportError: for any failure (workspace missing, parse error, …).
    """
    # ------------------------------------------------------------------
    # 1. Validate workspace
    # ------------------------------------------------------------------
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    if result.scalar_one_or_none() is None:
        raise SpecImportError(f"Workspace not found: {workspace_id}")

    # ------------------------------------------------------------------
    # 2. Generate storage key and write the raw file
    # ------------------------------------------------------------------
    ext = _storage_ext(filename)
    storage_key = f"{workspace_id}/specs/{uuid4()}.{ext}"

    await get_storage().write(storage_key, content)
    # NOTE: if anything below fails the file becomes orphaned.
    # TODO V1.5: add a reconciliation / cleanup job for orphaned storage files.

    # ------------------------------------------------------------------
    # 3. Create Spec row
    # ------------------------------------------------------------------
    spec = Spec(
        workspace_id=workspace_id,
        source=SpecSource.SWAGGER.value,
        # Provenance: upload → original_filename set, source_url None.
        #             URL    → source_url set, original_filename None.
        original_filename=filename if source_url is None else None,
        source_url=source_url,
        storage_key=storage_key,
        parsed_at=None,
    )
    db.add(spec)
    await db.flush()  # assign spec.id without committing

    # ------------------------------------------------------------------
    # 4. Parse
    # ------------------------------------------------------------------
    try:
        parsed_spec = await parse_swagger(
            content,
            raw_spec_ref=storage_key,
            filename=filename,
        )
    except ParserError as exc:
        # The storage file is already written — it will be orphaned when the
        # caller rolls back the DB transaction.
        # TODO V1.5: schedule orphaned-file cleanup.
        raise SpecImportError(f"Failed to parse spec: {exc}") from exc

    # ------------------------------------------------------------------
    # 5. Update spec, create Suite + Endpoints
    # ------------------------------------------------------------------
    spec.parsed_at = datetime.now(timezone.utc)

    suite = Suite(
        workspace_id=workspace_id,
        spec_id=spec.id,
        name=parsed_spec.title[:255],
        generation_status="parsed",
    )
    db.add(suite)
    await db.flush()  # assign suite.id

    endpoint_rows = [
        Endpoint(
            suite_id=suite.id,
            method=ep.method.value,
            path=ep.path,
            name=ep.name,
            description=ep.description,
            # Store the full ParsedEndpoint as JSONB — preserves all params,
            # schemas, auth info, and tags.  See Implementation Plan §11.2.
            endpoint_schema=ep.model_dump(mode="json"),
        )
        for ep in parsed_spec.endpoints
    ]
    db.add_all(endpoint_rows)

    # ------------------------------------------------------------------
    # 6. Commit
    # ------------------------------------------------------------------
    await db.commit()

    # ------------------------------------------------------------------
    # 7. Reload suite with eager-loaded endpoints and return
    # ------------------------------------------------------------------
    loaded = await db.execute(
        select(Suite)
        .where(Suite.id == suite.id)
        .options(selectinload(Suite.endpoints))
    )
    return loaded.scalar_one()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def import_from_upload(
    db: AsyncSession,
    workspace_id: UUID,
    content: bytes,
    filename: str,
) -> Suite:
    """Import a Swagger spec from uploaded file bytes.

    Args:
        db:           Caller-owned AsyncSession.
        workspace_id: Target workspace UUID.
        content:      Raw file bytes (JSON or YAML).
        filename:     Original filename (e.g. ``"petstore.json"``).

    Returns:
        The created :class:`~app.models.suite.Suite` with
        ``endpoints`` loaded.

    Raises:
        SpecImportError: on any failure.
    """
    return await _import_spec(
        db=db,
        workspace_id=workspace_id,
        content=content,
        filename=filename,
        source_url=None,
    )


async def import_from_url(
    db: AsyncSession,
    workspace_id: UUID,
    url: str,
) -> Suite:
    """Fetch a Swagger spec from *url* and import it.

    Args:
        db:           Caller-owned AsyncSession.
        workspace_id: Target workspace UUID.
        url:          Full HTTP(S) URL of the spec file.

    Returns:
        The created :class:`~app.models.suite.Suite` with
        ``endpoints`` loaded.

    Raises:
        SpecImportError: on fetch failure, parse failure, or DB error.
    """
    try:
        content, filename = await fetch_spec_from_url(url)
    except ParserError as exc:
        raise SpecImportError(f"Failed to fetch spec from {url!r}: {exc}") from exc

    return await _import_spec(
        db=db,
        workspace_id=workspace_id,
        content=content,
        filename=filename,
        source_url=url,
    )
