"""
Spec model — metadata for an imported API specification.

source values: 'SWAGGER' | 'POSTMAN' | 'CURL'

storage_key is a relative path under backend/storage/ in V1.
It becomes a MinIO object key in a later sprint when object storage is added.

parsed_at is null until the async parser worker finishes processing.
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Spec(Base):
    __tablename__ = "specs"

    __table_args__ = (
        sa.Index("ix_specs_workspace_id", "workspace_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(sa.String, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    source_url: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    storage_key: Mapped[str] = mapped_column(sa.String, nullable=False)
    parsed_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Spec id={self.id} source={self.source!r} workspace_id={self.workspace_id}>"
