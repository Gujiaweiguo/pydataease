from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visualization import DataVisualizationInfo
from app.repositories.base import AsyncBaseRepository


@final
class VisualizationRepository(AsyncBaseRepository[DataVisualizationInfo]):
    # pyright: ignore[reportGeneralTypeIssues]
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DataVisualizationInfo)

    async def list_all_ordered(self) -> Sequence[DataVisualizationInfo]:
        statement: Select[tuple[DataVisualizationInfo]] = select(DataVisualizationInfo).order_by(
            DataVisualizationInfo.sort.asc(),
            DataVisualizationInfo.update_time.desc(),
            DataVisualizationInfo.create_time.desc(),
        )
        return await self.get(statement)

    async def list_recent(self, size: int) -> Sequence[DataVisualizationInfo]:
        statement: Select[tuple[DataVisualizationInfo]] = (
            select(DataVisualizationInfo)
            .where((DataVisualizationInfo.delete_flag.is_(False)) | (DataVisualizationInfo.delete_flag.is_(None)))
            .order_by(DataVisualizationInfo.update_time.desc(), DataVisualizationInfo.create_time.desc())
            .limit(size)
        )
        return await self.get(statement)
