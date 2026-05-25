"""
Suite model — a named collection of endpoints extracted from a spec.

generation_status values: 'pending' | 'parsing' | 'parsed' | 'failed'

A suite transitions pending → parsing → parsed (or failed) as the
async worker processes the parent spec.
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Suite(Base):
    __tablename__ = "suites"

    __table_args__ = (
        sa.Index("ix_suites_workspace_id", "workspace_id"),
        sa.Index("ix_suites_spec_id", "spec_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    spec_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("specs.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    generation_status: Mapped[str] = mapped_column(
        sa.String,
        nullable=False,
        server_default=sa.text("'pending'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Suite id={self.id} name={self.name!r} "
            f"status={self.generation_status!r}>"
        )
