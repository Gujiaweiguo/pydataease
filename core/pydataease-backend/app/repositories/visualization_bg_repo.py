from __future__ import annotations

from typing import final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visualization_background import VisualizationBackground
from app.repositories.base import AsyncBaseRepository


@final
class VisualizationBackgroundRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, VisualizationBackground)
        self.session = session

    async def list_all(self) -> list[VisualizationBackground]:
        stmt = select(VisualizationBackground)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
