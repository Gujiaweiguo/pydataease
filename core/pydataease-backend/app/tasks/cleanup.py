from __future__ import annotations

import logging
import os
import time

from app.dependencies.database import async_session
from app.repositories.export_repo import ExportTaskRepository
from app.repositories.share_repo import ShareRepository

logger = logging.getLogger(__name__)

_DEFAULT_EXPORT_RETENTION_MS = 7 * 24 * 60 * 60 * 1000  # 7 days


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


async def cleanup_expired_shares() -> None:
    now_ms = int(time.time() * 1000)
    async with async_session() as session:
        repo = ShareRepository(session)
        count = await repo.delete_expired(now_ms)
    logger.info("Cleaned up %d expired shares", count)


async def cleanup_old_export_tasks() -> None:
    now_ms = int(time.time() * 1000)
    retention_ms = _env_int("DE_EXPORT_RETENTION_MS", _DEFAULT_EXPORT_RETENTION_MS)
    before_ms = now_ms - retention_ms
    async with async_session() as session:
        repo = ExportTaskRepository(session)
        count = await repo.delete_old_completed(before_ms)
    logger.info("Cleaned up %d old export tasks", count)
