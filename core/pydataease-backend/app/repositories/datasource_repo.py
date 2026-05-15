from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.datasource import CoreDatasource
from app.repositories.base import AsyncBaseRepository


@final
class DatasourceRepository(AsyncBaseRepository[CoreDatasource]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoreDatasource)

    async def search(self, keyword: str) -> Sequence[CoreDatasource]:
        statement: Select[tuple[CoreDatasource]] = select(CoreDatasource).order_by(CoreDatasource.update_time.desc())
        if keyword and keyword != "_":
            wildcard = f"%{keyword}%"
            statement = statement.where(
                or_(
                    CoreDatasource.name.ilike(wildcard),
                    CoreDatasource.description.ilike(wildcard),
                    CoreDatasource.type.ilike(wildcard),
                )
            )
        return await self.get(statement)

    async def get_by_name(self, name: str) -> CoreDatasource | None:
        statement: Select[tuple[CoreDatasource]] = select(CoreDatasource).where(CoreDatasource.name == name).limit(1)
        result = await self.session.execute(statement)
        return result.scalars().first()
