from __future__ import annotations

from collections.abc import Sequence
from typing import Any, final

from sqlalchemy import delete, select, update
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
        # Always clear tables for this node (no-op if none exist)
        await self._delete_dataset_tables(pid)
        stmt = delete(CoreDatasetGroup).where(CoreDatasetGroup.id == pid)
        await self.session.execute(stmt)
        await self.session.commit()

    async def _delete_dataset_tables(self, dataset_group_id: int) -> None:
        # Clear FK references to datasource before deleting
        clear_table_fk = (
            update(CoreDatasetTable)
            .where(CoreDatasetTable.dataset_group_id == dataset_group_id)
            .values(datasource_id=None)
        )
        await self.session.execute(clear_table_fk)
        clear_field_fk = (
            update(CoreDatasetTableField)
            .where(CoreDatasetTableField.dataset_group_id == dataset_group_id)
            .values(datasource_id=None)
        )
        await self.session.execute(clear_field_fk)
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

    async def get_by_datasource_and_table(self, datasource_id: int, table_name: str) -> CoreDatasetTable | None:
        stmt = select(CoreDatasetTable).where(
            CoreDatasetTable.datasource_id == datasource_id,
            CoreDatasetTable.table_name == table_name,
        )
        rows = await self.get(stmt)
        return rows[0] if rows else None


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

    async def list_checked_by_group(self, dataset_group_id: int) -> Sequence[CoreDatasetTableField]:
        stmt = (
            select(CoreDatasetTableField)
            .where(
                CoreDatasetTableField.dataset_group_id == dataset_group_id,
                CoreDatasetTableField.checked == True,  # noqa: E712
                CoreDatasetTableField.chart_id.is_(None),
            )
            .order_by(CoreDatasetTableField.column_index.asc())
        )
        return await self.get(stmt)

    async def list_checked_by_group_no_chart_filter(self, dataset_group_id: int) -> Sequence[CoreDatasetTableField]:
        stmt = (
            select(CoreDatasetTableField)
            .where(
                CoreDatasetTableField.dataset_group_id == dataset_group_id,
                CoreDatasetTableField.checked == True,  # noqa: E712
            )
            .order_by(CoreDatasetTableField.column_index.asc())
        )
        return await self.get(stmt)

    async def delete_by_id(self, field_id: int) -> None:
        stmt = delete(CoreDatasetTableField).where(CoreDatasetTableField.id == field_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_by_chart_id(self, chart_id: int) -> None:
        stmt = delete(CoreDatasetTableField).where(CoreDatasetTableField.chart_id == chart_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def list_origin_fields_by_groups(self, group_ids: list[int]) -> dict[str, list[Any]]:
        result: dict[str, list[Any]] = {}
        for gid in group_ids:
            stmt = (
                select(CoreDatasetTableField)
                .where(
                    CoreDatasetTableField.dataset_group_id == gid,
                    CoreDatasetTableField.checked == True,  # noqa: E712
                    CoreDatasetTableField.chart_id.is_(None),
                    CoreDatasetTableField.ext_field == 0,
                )
                .order_by(CoreDatasetTableField.column_index.asc())
            )
            rows = await self.get(stmt)
            result[str(gid)] = list(rows)
        return result

    async def save_field(self, field_data: dict[str, object]) -> CoreDatasetTableField:
        field_id = field_data.get("id")
        if field_id:
            existing = await self.session.get(CoreDatasetTableField, field_id)
            if existing:
                for key, value in field_data.items():
                    setattr(existing, key, value)
                await self.session.commit()
                await self.session.refresh(existing)
                return existing
        entity = CoreDatasetTableField(**field_data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
