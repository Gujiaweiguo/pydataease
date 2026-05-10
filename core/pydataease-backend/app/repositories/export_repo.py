from __future__ import annotations

from typing import final

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export import CoreExportTask
from app.repositories.base import AsyncBaseRepository


@final
class ExportTaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, CoreExportTask)
        self.session = session

    async def get_by_id(self, task_id: str) -> CoreExportTask | None:
        return await self.session.get(CoreExportTask, task_id)

    async def list_by_user_and_from(
        self, user_id: int, export_from: int
    ) -> list[CoreExportTask]:
        stmt = (
            select(CoreExportTask)
            .where(
                CoreExportTask.user_id == user_id,
                CoreExportTask.export_from == export_from,
            )
            .order_by(CoreExportTask.export_time.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, payload: dict[str, object]) -> CoreExportTask:
        return await self._base.create(payload)

    async def delete_by_id(self, task_id: str) -> None:
        stmt = delete(CoreExportTask).where(CoreExportTask.id == task_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all_by_user_and_from(
        self, user_id: int, export_from: int
    ) -> None:
        stmt = delete(CoreExportTask).where(
            CoreExportTask.user_id == user_id,
            CoreExportTask.export_from == export_from,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_old_completed(self, before_ms: int) -> int:
        stmt = (
            delete(CoreExportTask)
            .where(
                CoreExportTask.export_status.in_(["SUCCESS", "FAILED"]),
                CoreExportTask.export_time < before_ms,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
