from __future__ import annotations

import time
from typing import final

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.role import CoreRole
from ..models.role_user import CoreRoleUser
from ..models.user import CoreUser
from .base import AsyncBaseRepository


@final
class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, CoreRole)
        self.session = session

    async def get_by_id(self, role_id: int) -> CoreRole | None:
        return await self._base.get_by_id(role_id)

    async def list_by_org(self, oid: int) -> list[CoreRole]:
        stmt = select(CoreRole).where(or_(CoreRole.oid == 0, CoreRole.oid == oid)).order_by(CoreRole.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, payload: dict[str, object]) -> CoreRole:
        return await self._base.create(payload)

    async def update(self, entity: CoreRole, payload: dict[str, object]) -> CoreRole:
        return await self._base.update(entity, payload)

    async def delete(self, entity: CoreRole) -> None:
        await self._base.delete(entity)

    async def get_user_roles(self, user_id: int, oid: int) -> list[CoreRole]:
        stmt = (
            select(CoreRole)
            .join(CoreRoleUser, CoreRoleUser.role_id == CoreRole.id)
            .where(CoreRoleUser.user_id == user_id, CoreRoleUser.oid == oid)
            .order_by(CoreRole.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_role_users(self, role_id: int) -> list[CoreUser]:
        stmt = (
            select(CoreUser)
            .join(CoreRoleUser, CoreRoleUser.user_id == CoreUser.id)
            .where(CoreRoleUser.role_id == role_id)
            .order_by(CoreUser.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def is_user_in_role(self, user_id: int, role_id: int, oid: int) -> bool:
        stmt = (
            select(CoreRoleUser.id)
            .where(CoreRoleUser.user_id == user_id, CoreRoleUser.role_id == role_id, CoreRoleUser.oid == oid)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def bind_user(self, role_id: int, user_id: int, oid: int) -> CoreRoleUser:
        entity = CoreRoleUser(id=int(time.time_ns()), role_id=role_id, user_id=user_id, oid=oid)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def unbind_user(self, role_id: int, user_id: int, oid: int) -> None:
        stmt = delete(CoreRoleUser).where(
            CoreRoleUser.role_id == role_id,
            CoreRoleUser.user_id == user_id,
            CoreRoleUser.oid == oid,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def count_members_batch(self, role_ids: list[int]) -> dict[int, int]:
        if not role_ids:
            return {}
        stmt = (
            select(CoreRoleUser.role_id, func.count(CoreRoleUser.id))
            .where(CoreRoleUser.role_id.in_(role_ids))
            .group_by(CoreRoleUser.role_id)
        )
        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
