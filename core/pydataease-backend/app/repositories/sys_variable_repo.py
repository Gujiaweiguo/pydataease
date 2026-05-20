from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import Select, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sys_variable import CoreSysVariable, CoreSysVariableValue
from app.repositories.base import AsyncBaseRepository


def _like_pattern(keyword: str) -> str:
    return f"%{keyword.strip()}%"


@final
class SysVariableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._base = AsyncBaseRepository(session, CoreSysVariable)

    async def get_by_id(self, variable_id: int) -> CoreSysVariable | None:
        return await self._base.get_by_id(variable_id)

    async def create(self, payload: dict[str, object]) -> CoreSysVariable:
        return await self._base.create(payload)

    async def update(self, entity: CoreSysVariable, payload: dict[str, object]) -> CoreSysVariable:
        return await self._base.update(entity, payload)

    async def delete(self, entity: CoreSysVariable) -> None:
        await self._base.delete(entity)

    async def search(self, keyword: str | None = None, name: str | None = None, type_: str | None = None) -> Sequence[CoreSysVariable]:
        stmt: Select[tuple[CoreSysVariable]] = select(CoreSysVariable)
        filters = []
        if keyword:
            pattern = _like_pattern(keyword)
            filters.append(
                or_(
                    CoreSysVariable.name.ilike(pattern),
                    CoreSysVariable.alias.ilike(pattern),
                    CoreSysVariable.remark.ilike(pattern),
                )
            )
        if name:
            filters.append(CoreSysVariable.name.ilike(_like_pattern(name)))
        if type_:
            filters.append(CoreSysVariable.type == type_)
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.order_by(CoreSysVariable.create_time.desc(), CoreSysVariable.id.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()


@final
class SysVariableValueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._base = AsyncBaseRepository(session, CoreSysVariableValue)

    async def get_by_id(self, value_id: int) -> CoreSysVariableValue | None:
        return await self._base.get_by_id(value_id)

    async def create(self, payload: dict[str, object]) -> CoreSysVariableValue:
        return await self._base.create(payload)

    async def update(self, entity: CoreSysVariableValue, payload: dict[str, object]) -> CoreSysVariableValue:
        return await self._base.update(entity, payload)

    async def delete(self, entity: CoreSysVariableValue) -> None:
        await self._base.delete(entity)

    async def list_by_variable_id(self, variable_id: int) -> Sequence[CoreSysVariableValue]:
        stmt = (
            select(CoreSysVariableValue)
            .where(CoreSysVariableValue.variable_id == variable_id)
            .order_by(CoreSysVariableValue.create_time.desc(), CoreSysVariableValue.id.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def page_by_variable_id(
        self,
        variable_id: int | None,
        keyword: str | None,
        offset: int,
        limit: int,
    ) -> tuple[Sequence[CoreSysVariableValue], int]:
        stmt = select(CoreSysVariableValue)
        count_stmt = select(func.count()).select_from(CoreSysVariableValue)
        filters = []
        if variable_id is not None:
            filters.append(CoreSysVariableValue.variable_id == variable_id)
        if keyword:
            pattern = _like_pattern(keyword)
            filters.append(
                or_(
                    CoreSysVariableValue.value.ilike(pattern),
                    CoreSysVariableValue.name.ilike(pattern),
                    CoreSysVariableValue.remark.ilike(pattern),
                )
            )
        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)
        stmt = stmt.order_by(CoreSysVariableValue.create_time.desc(), CoreSysVariableValue.id.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        total_result = await self.session.execute(count_stmt)
        return result.scalars().all(), int(total_result.scalar_one())

    async def delete_by_variable_id(self, variable_id: int) -> None:
        await self.session.execute(delete(CoreSysVariableValue).where(CoreSysVariableValue.variable_id == variable_id))
        await self.session.commit()

    async def batch_delete(self, ids: list[int]) -> None:
        if not ids:
            return
        await self.session.execute(delete(CoreSysVariableValue).where(CoreSysVariableValue.id.in_(ids)))
        await self.session.commit()
