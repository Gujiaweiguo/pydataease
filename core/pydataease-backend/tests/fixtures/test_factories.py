"""Shared test factory helpers."""
from __future__ import annotations

import time

from sqlalchemy.ext.asyncio import AsyncSession


def stamp() -> int:
    """Generate a unique BigInteger ID using time.time_ns()."""
    return time.time_ns()


def timestamp_ms() -> int:
    """Current time in milliseconds."""
    return int(time.time() * 1000)


async def cleanup_groups(session: AsyncSession, ids: list[int]) -> None:
    """Delete dataset groups in reverse order (children first)."""
    from app.repositories.dataset_repo import DatasetGroupRepository  # pyright: ignore[reportImplicitRelativeImport]

    repo = DatasetGroupRepository(session)
    for gid in reversed(ids):
        try:
            await repo.delete_cascade(gid)
        except Exception:
            pass
