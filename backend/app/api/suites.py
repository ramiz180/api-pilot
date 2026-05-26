"""Suite endpoints.

GET /api/suites           — list suites in the current workspace
GET /api/suites/{suite_id} — get suite detail with endpoint list
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_workspace_id, get_db
from app.schemas.api import SuiteDetailOut, SuiteSummaryOut
from app.services import SuiteNotFoundError
from app.services import suite_service

router = APIRouter()


@router.get(
    "/suites",
    response_model=list[SuiteSummaryOut],
    summary="List suites in the current workspace",
)
async def list_suites(
    workspace_id: UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db),
) -> list[SuiteSummaryOut]:
    """Return all suites for the current workspace, newest first.

    Each item includes an ``endpoint_count`` — no endpoint list in this view.
    """
    suites = await suite_service.list_suites(db=db, workspace_id=workspace_id)
    return [SuiteSummaryOut.model_validate(s) for s in suites]


@router.get(
    "/suites/{suite_id}",
    response_model=SuiteDetailOut,
    summary="Get suite detail",
)
async def get_suite(
    suite_id: UUID,
    workspace_id: UUID = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db),
) -> SuiteDetailOut:
    """Return a single suite with its endpoint list.

    Each endpoint includes ``id``, ``method``, ``path``, ``name``, and
    ``description`` — the full ``schema`` blob is omitted (use
    GET /api/endpoints/{id} for that, Sprint 1d).

    Raises HTTP 404 if the suite does not exist or belongs to a different
    workspace.
    """
    try:
        suite = await suite_service.get_suite(
            db=db,
            suite_id=suite_id,
            workspace_id=workspace_id,
        )
    except SuiteNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Suite not found") from exc

    return SuiteDetailOut.model_validate(suite)
