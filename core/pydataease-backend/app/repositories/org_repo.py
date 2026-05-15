from __future__ import annotations

from typing import final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.org import CoreOrg
from ..models.user import CoreUser
from ..models.user_org import CoreUserOrg
from .base import AsyncBaseRepository


@final
class OrgRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, CoreOrg)
        self.session = session

    async def get_by_id(self, org_id: int) -> CoreOrg | None:
        return await self._base.get_by_id(org_id)

    async def list_all(self) -> list[CoreOrg]:
        stmt = select(CoreOrg).order_by(CoreOrg.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, pid: int) -> list[CoreOrg]:
        stmt = select(CoreOrg).where(CoreOrg.pid == pid).order_by(CoreOrg.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, payload: dict[str, object]) -> CoreOrg:
        return await self._base.create(payload)

    async def update(self, entity: CoreOrg, payload: dict[str, object]) -> CoreOrg:
        return await self._base.update(entity, payload)

    async def delete(self, entity: CoreOrg) -> None:
        await self._base.delete(entity)

    async def get_user_orgs(self, user_id: int) -> list[CoreOrg]:
        stmt = (
            select(CoreOrg)
            .join(CoreUserOrg, CoreUserOrg.org_id == CoreOrg.id)
            .where(CoreUserOrg.user_id == user_id)
            .order_by(CoreOrg.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def is_member(self, user_id: int, org_id: int) -> bool:
        stmt = select(CoreUserOrg.id).where(CoreUserOrg.user_id == user_id, CoreUserOrg.org_id == org_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_org_users(self, org_id: int) -> list[CoreUser]:
        stmt = (
            select(CoreUser)
            .join(CoreUserOrg, CoreUserOrg.user_id == CoreUser.id)
            .where(CoreUserOrg.org_id == org_id)
            .order_by(CoreUser.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
