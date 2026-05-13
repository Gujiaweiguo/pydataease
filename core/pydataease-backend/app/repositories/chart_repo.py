from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import Select, delete, select
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

    async def upsert_by_id(self, chart_data: dict[str, object]) -> CoreChartView:
        chart_id = chart_data.get("id")
        if not isinstance(chart_id, int):
            raise TypeError("chart_data.id must be int")
        existing = await self.get_by_id(chart_id)
        if existing is not None:
            return await self.update(existing, chart_data)
        return await self.create(chart_data)

    async def delete_by_scene_excluding(self, scene_id: int, keep_ids: set[int]) -> None:
        statement = delete(CoreChartView).where(CoreChartView.scene_id == scene_id)
        if keep_ids:
            statement = statement.where(CoreChartView.id.not_in(keep_ids))
        await self.session.execute(statement)
        await self.session.commit()
