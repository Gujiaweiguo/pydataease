from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import CoreChartView
from app.repositories.base import AsyncBaseRepository


@final
class ChartRepository(AsyncBaseRepository[CoreChartView]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoreChartView)

    async def list_by_scene(self, scene_id: int) -> Sequence[CoreChartView]:
        statement: Select[tuple[CoreChartView]] = (
            select(CoreChartView)
            .where(CoreChartView.scene_id == scene_id)
            .order_by(CoreChartView.update_time.desc(), CoreChartView.create_time.desc())
        )
        return await self.get(statement)
