from __future__ import annotations

from typing import final

from sqlalchemy import delete, func, select
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

    async def list_by_user(self, user_id: int) -> list[CoreExportTask]:
        stmt = (
            select(CoreExportTask)
            .where(CoreExportTask.user_id == user_id)
            .order_by(CoreExportTask.export_time.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user_grouped_by_status(self, user_id: int) -> dict[str, int]:
        stmt = (
            select(CoreExportTask.export_status, func.count(CoreExportTask.id))
            .where(CoreExportTask.user_id == user_id)
            .group_by(CoreExportTask.export_status)
        )
        result = await self.session.execute(stmt)
        counts = {str(status): int(count) for status, count in result.all()}
        all_count = sum(counts.values())
        return {
            "ALL": all_count,
            "IN_PROGRESS": counts.get("RUNNING", 0) + counts.get("INITIATED", 0),
            "SUCCESS": counts.get("SUCCESS", 0),
            "FAILED": counts.get("FAILED", 0),
            "PENDING": counts.get("INITIATED", 0),
        }

    async def list_paginated_by_user_and_status(
        self,
        user_id: int,
        status: str,
        offset: int,
        limit: int,
    ) -> tuple[int, list[CoreExportTask]]:
        normalized = status.upper()
        base_conditions = [CoreExportTask.user_id == user_id]
        if normalized == "SUCCESS":
            base_conditions.append(CoreExportTask.export_status == "SUCCESS")
        elif normalized == "FAILED":
            base_conditions.append(CoreExportTask.export_status == "FAILED")
        elif normalized == "PENDING":
            base_conditions.append(CoreExportTask.export_status == "INITIATED")
        elif normalized == "IN_PROGRESS":
            base_conditions.append(CoreExportTask.export_status.in_(["INITIATED", "RUNNING"]))

        count_stmt = select(func.count(CoreExportTask.id)).where(*base_conditions)
        total = int((await self.session.execute(count_stmt)).scalar_one() or 0)

        stmt = (
            select(CoreExportTask)
            .where(*base_conditions)
            .order_by(CoreExportTask.export_time.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return total, list(result.scalars().all())

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

    async def delete_all_by_user_and_status(self, user_id: int, status: str) -> None:
        normalized = status.upper()
        conditions = [CoreExportTask.user_id == user_id]
        if normalized == "SUCCESS":
            conditions.append(CoreExportTask.export_status == "SUCCESS")
        elif normalized == "FAILED":
            conditions.append(CoreExportTask.export_status == "FAILED")
        elif normalized == "PENDING":
            conditions.append(CoreExportTask.export_status == "INITIATED")
        elif normalized == "IN_PROGRESS":
            conditions.append(CoreExportTask.export_status.in_(["INITIATED", "RUNNING"]))
        stmt = delete(CoreExportTask).where(*conditions)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_by_ids(self, user_id: int, ids: list[str]) -> None:
        if not ids:
            return
        stmt = delete(CoreExportTask).where(
            CoreExportTask.user_id == user_id,
            CoreExportTask.id.in_(ids),
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
