from __future__ import annotations

from typing import final

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import CoreUser
from app.models.user_org import CoreUserOrg
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

    async def search(
        self,
        keyword: str | None,
        enable: bool | None,
        oid: int | None,
        offset: int,
        limit: int,
    ) -> tuple[list[CoreUser], int]:
        stmt = select(CoreUser)
        count_stmt: Select[tuple[int]] = select(func.count()).select_from(CoreUser)

        if oid not in (None, 0):
            stmt = stmt.join(CoreUserOrg, CoreUserOrg.user_id == CoreUser.id).where(CoreUserOrg.org_id == oid)
            count_stmt = (
                select(func.count(func.distinct(CoreUser.id)))
                .select_from(CoreUser)
                .join(CoreUserOrg, CoreUserOrg.user_id == CoreUser.id)
                .where(CoreUserOrg.org_id == oid)
            )

        stmt, count_stmt = self._apply_filters(stmt, count_stmt, keyword=keyword, enable=enable)
        stmt = stmt.order_by(CoreUser.id).offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        total_result = await self.session.execute(count_stmt)
        return list(result.scalars().all()), int(total_result.scalar_one())

    async def delete(self, entity: CoreUser) -> None:
        await self._base.delete(entity)

    @staticmethod
    def _apply_filters(
        stmt: Select[tuple[CoreUser]],
        count_stmt: Select[tuple[int]],
        *,
        keyword: str | None,
        enable: bool | None,
    ) -> tuple[Select[tuple[CoreUser]], Select[tuple[int]]]:
        conditions = []
        cleaned_keyword = keyword.strip() if keyword else ""
        if cleaned_keyword:
            like_value = f"%{cleaned_keyword}%"
            conditions.append(
                or_(
                    CoreUser.account.ilike(like_value),
                    CoreUser.name.ilike(like_value),
                    CoreUser.email.ilike(like_value),
                    CoreUser.phone.ilike(like_value),
                )
            )
        if enable is not None:
            conditions.append(CoreUser.enable.is_(enable))
        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)
        return stmt, count_stmt
