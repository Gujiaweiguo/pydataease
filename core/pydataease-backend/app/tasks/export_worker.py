from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.export import CoreExportTask
from app.repositories.export_repo import ExportTaskRepository
from app.tasks.base import idempotent_task_check, with_retry

logger = logging.getLogger(__name__)


@final
class ExportTaskWorker:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        sleep_seconds: float = 0.05,
        time_provider: Callable[[], int] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._sleep_seconds = sleep_seconds
        self._time_provider = time_provider or (lambda: int(time.time() * 1000))

    async def run_pending_exports(self) -> None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CoreExportTask.id)
                .where(CoreExportTask.export_status == "INITIATED")
                .order_by(CoreExportTask.export_time.asc())
            )
            task_ids = list(result.scalars().all())
        for task_id in task_ids:
            await self.run_task(task_id)

    async def retry_task(self, task_id: str) -> bool:
        async with self._session_factory() as session:
            repo = ExportTaskRepository(session)
            task = await repo.get_by_id(task_id)
            if task is None or task.export_status != "FAILED":
                return False
            task.export_status = "INITIATED"
            task.export_progress = "0"
            task.msg = None
            task.export_time = self._time_provider()
            await session.commit()
        await self.run_task(task_id)
        return True

    async def run_task(self, task_id: str) -> bool:
        async with self._session_factory() as session:
            if not await idempotent_task_check(task_id, session):
                return False
        try:
            await self._execute_with_retry(task_id)
        except Exception as exc:
            await self._mark_failed(task_id, str(exc))
            logger.exception("export task failed after retries: %s", task_id)
            return False
        return True

    @with_retry(max_retries=3, backoff_base=0.1)
    async def _execute_with_retry(self, task_id: str) -> None:
        await self._mark_running(task_id)
        await asyncio.sleep(self._sleep_seconds)
        await self._mark_success(task_id)

    async def _mark_running(self, task_id: str) -> None:
        async with self._session_factory() as session:
            repo = ExportTaskRepository(session)
            task = await repo.get_by_id(task_id)
            if task is None:
                raise ValueError("Export task not found")
            if task.export_status in {"RUNNING", "SUCCESS"}:
                return
            task.export_status = "RUNNING"
            task.export_progress = "10"
            task.msg = None
            await session.commit()

    async def _mark_success(self, task_id: str) -> None:
        async with self._session_factory() as session:
            repo = ExportTaskRepository(session)
            task = await repo.get_by_id(task_id)
            if task is None:
                raise ValueError("Export task not found")
            task.export_status = "SUCCESS"
            task.export_progress = "100"
            task.msg = "Export task completed"
            await session.commit()

    async def _mark_failed(self, task_id: str, message: str) -> None:
        async with self._session_factory() as session:
            repo = ExportTaskRepository(session)
            task = await repo.get_by_id(task_id)
            if task is None:
                return
            task.export_status = "FAILED"
            task.msg = message
            await session.commit()
