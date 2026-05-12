from __future__ import annotations

from typing import final

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import CoreDatasetGroup, CoreDatasetTable, CoreDatasetTableField
from app.repositories.base import AsyncBaseRepository


@final
class DatasetGroupRepository(AsyncBaseRepository[CoreDatasetGroup]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoreDatasetGroup)

    async def list_all_ordered(self) -> Sequence[CoreDatasetGroup]:
        stmt = select(CoreDatasetGroup).where(CoreDatasetGroup.id != 0).order_by(
            CoreDatasetGroup.name.asc(),
            CoreDatasetGroup.create_time.desc(),
        )
        return await self.get(stmt)

    async def get_children(self, pid: int) -> Sequence[CoreDatasetGroup]:
        stmt = (
            select(CoreDatasetGroup)
            .where(CoreDatasetGroup.pid == pid)
            .order_by(CoreDatasetGroup.name.asc())
        )
        return await self.get(stmt)

    async def delete_cascade(self, group_id: int) -> None:
        await self._delete_descendants(group_id)

    async def _delete_descendants(self, pid: int) -> None:
        children = await self.get_children(pid)
        for child in children:
            await self._delete_descendants(child.id)
            if child.node_type == "dataset":
                await self._delete_dataset_tables(child.id)
        stmt = delete(CoreDatasetGroup).where(CoreDatasetGroup.id == pid)
        await self.session.execute(stmt)
        await self.session.commit()

    async def _delete_dataset_tables(self, dataset_group_id: int) -> None:
        field_stmt = delete(CoreDatasetTableField).where(
            CoreDatasetTableField.dataset_group_id == dataset_group_id
        )
        await self.session.execute(field_stmt)
        table_stmt = delete(CoreDatasetTable).where(
            CoreDatasetTable.dataset_group_id == dataset_group_id
        )
        await self.session.execute(table_stmt)
        await self.session.commit()


@final
class DatasetTableRepository(AsyncBaseRepository[CoreDatasetTable]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoreDatasetTable)

    async def list_by_group(self, dataset_group_id: int) -> Sequence[CoreDatasetTable]:
        stmt = select(CoreDatasetTable).where(
            CoreDatasetTable.dataset_group_id == dataset_group_id
        )
        return await self.get(stmt)


@final
class DatasetFieldRepository(AsyncBaseRepository[CoreDatasetTableField]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoreDatasetTableField)

    async def list_by_table(self, dataset_table_id: int) -> Sequence[CoreDatasetTableField]:
        stmt = (
            select(CoreDatasetTableField)
            .where(CoreDatasetTableField.dataset_table_id == dataset_table_id)
            .order_by(CoreDatasetTableField.column_index.asc())
        )
        return await self.get(stmt)

    async def list_by_group(self, dataset_group_id: int) -> Sequence[CoreDatasetTableField]:
        stmt = (
            select(CoreDatasetTableField)
            .where(CoreDatasetTableField.dataset_group_id == dataset_group_id)
            .order_by(CoreDatasetTableField.column_index.asc())
        )
        return await self.get(stmt)

    async def delete_by_group(self, dataset_group_id: int) -> None:
        stmt = delete(CoreDatasetTableField).where(
            CoreDatasetTableField.dataset_group_id == dataset_group_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
