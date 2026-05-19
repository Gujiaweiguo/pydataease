"""Shared database fixtures for integration tests."""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

PG_URL = os.environ.get(
    "DE_DATABASE_URL",
    "postgresql+asyncpg://dataease:dataease@127.0.0.1:5432/dataease",
)


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(PG_URL)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()
