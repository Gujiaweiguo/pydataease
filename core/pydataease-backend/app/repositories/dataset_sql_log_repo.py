from __future__ import annotations

from typing import final

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset_sql_log import DatasetTableSqlLog


@final
class DatasetSqlLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_table_id(self, table_id: str) -> list[DatasetTableSqlLog]:
        result = await self.session.execute(
            select(DatasetTableSqlLog).where(DatasetTableSqlLog.table_id == table_id)
        )
        return list(result.scalars().all())

    async def create(self, payload: dict[str, object]) -> DatasetTableSqlLog:
        entity = DatasetTableSqlLog(**payload)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete_by_table_id(self, table_id: str) -> None:
        await self.session.execute(
            delete(DatasetTableSqlLog).where(DatasetTableSqlLog.table_id == table_id)
        )
        await self.session.commit()
