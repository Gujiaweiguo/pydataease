from __future__ import annotations

from typing import final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import CoreUser
from app.repositories.base import AsyncBaseRepository


@final
class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, CoreUser)
        self.session = session

    async def get_by_id(self, user_id: int) -> CoreUser | None:
        return await self._base.get_by_id(user_id)

    async def get_by_account(self, account: str) -> CoreUser | None:
        stmt = select(CoreUser).where(CoreUser.account == account).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, payload: dict[str, object]) -> CoreUser:
        return await self._base.create(payload)

    async def update(self, entity: CoreUser, payload: dict[str, object]) -> CoreUser:
        return await self._base.update(entity, payload)

    async def list_all(self) -> list[CoreUser]:
        return list(await self._base.list())
