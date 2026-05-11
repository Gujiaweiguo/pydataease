from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import CoreStore
from app.repositories.base import AsyncBaseRepository


@final
class StoreRepository(AsyncBaseRepository[CoreStore]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoreStore)

    async def get_by_resource(self, resource_id: int, uid: int, resource_type: int) -> CoreStore | None:
        statement: Select[tuple[CoreStore]] = select(CoreStore).where(
            CoreStore.resource_id == resource_id,
            CoreStore.uid == uid,
            CoreStore.resource_type == resource_type,
        ).limit(1)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def query_by_user(self, uid: int, resource_type: int | None = None) -> Sequence[CoreStore]:
        stmt = select(CoreStore).where(CoreStore.uid == uid).order_by(CoreStore.time.desc())
        if resource_type is not None:
            stmt = stmt.where(CoreStore.resource_type == resource_type)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_by_resource(self, resource_id: int, uid: int, resource_type: int) -> None:
        statement = delete(CoreStore).where(
            CoreStore.resource_id == resource_id,
            CoreStore.uid == uid,
            CoreStore.resource_type == resource_type,
        )
        await self.session.execute(statement)
        await self.session.commit()
