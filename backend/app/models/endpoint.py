"""
Endpoint model — a single parsed API endpoint within a suite.

method values: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

The `endpoint_schema` JSONB column holds the full parsed shape from the
parser layer (§6.2 of the Implementation Plan):
    {
        "path_params":        [...],
        "query_params":       [...],
        "headers":            [...],
        "body_schema":        {...} | null,
        "response_schemas":   {"200": {...}, "404": {...}, ...},
        "auth":               {...} | null,
        "tags":               [...]
    }

Column is named `endpoint_schema` in Python (avoids collision with
SQLAlchemy's internal `.schema` attribute on Table objects) but stored
as `schema` in the database to match the spec.
"""

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Endpoint(Base):
    __tablename__ = "endpoints"

    __table_args__ = (
        sa.Index("ix_endpoints_suite_id", "suite_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    suite_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("suites.id", ondelete="CASCADE"),
        nullable=False,
    )
    method: Mapped[str] = mapped_column(sa.String, nullable=False)
    path: Mapped[str] = mapped_column(sa.String, nullable=False)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    # Stored as `schema` in Postgres; Python attribute is `endpoint_schema`
    # to avoid collision with SQLAlchemy's Table.schema internal attribute.
    endpoint_schema: Mapped[dict[str, Any]] = mapped_column(
        "schema", JSONB, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Endpoint id={self.id} method={self.method!r} path={self.path!r}>"
