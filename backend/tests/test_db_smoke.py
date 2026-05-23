"""
Async DB smoke test — runs against in-memory SQLite (aiosqlite).

This test proves the async engine + Base setup works without requiring
a live Postgres instance.  Postgres integration tests come in a later sprint
once Docker Compose is running (Prompt 4+).
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base


@pytest.fixture
async def sqlite_engine():
    """Create a fresh in-memory async SQLite engine for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        # Create all tables defined on Base (currently none — that's fine)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(sqlite_engine):
    """Yield an AsyncSession bound to the in-memory SQLite engine."""
    factory = async_sessionmaker(
        bind=sqlite_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session


async def test_db_select_one(db_session: AsyncSession):
    """Trivial query — proves the async session pipeline works end-to-end."""
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar_one()
    assert value == 1


async def test_base_metadata_is_empty():
    """Base.metadata has no tables yet — models are added in Sprint 1."""
    assert isinstance(Base.metadata.tables, dict)
    # Empty for now; this assertion will change once real models are added
    assert len(Base.metadata.tables) == 0
