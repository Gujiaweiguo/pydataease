from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.chart import CoreChartView
from app.repositories.chart_repo import ChartRepository
from app.repositories.dataset_repo import DatasetFieldRepository
from app.schemas.auth import TokenUser
from app.schemas.chart import (
    ChartDataRequest,
    ChartDataResponse,
    ChartDetailResponse,
    ChartFieldResponse,
    ChartResponse,
    ChartSaveRequest,
    ChartUpdateRequest,
)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


@final
class ChartService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chart_repo = ChartRepository(session)
        self.field_repo = DatasetFieldRepository(session)

    async def get_by_id(self, chart_id: int) -> ChartResponse:
        chart = await self._get_chart(chart_id)
        return ChartResponse.model_validate(chart)

    async def save(self, payload: ChartSaveRequest, user: TokenUser) -> ChartResponse:
        now = _timestamp_ms()
        created = await self.chart_repo.create({
            **payload.model_dump(by_alias=False, exclude_none=True),
            "id": payload.id or _new_identifier(),
            "create_by": str(user.user_id),
            "create_time": now,
            "update_time": now,
        })
        return ChartResponse.model_validate(created)

    async def update(self, payload: ChartUpdateRequest, user: TokenUser) -> ChartResponse:
        existing = await self._get_chart(payload.id)
        update_data = payload.model_dump(by_alias=False, exclude_none=True)
        update_data["update_time"] = _timestamp_ms()
        update_data.setdefault("create_by", existing.create_by)
        _ = user
        updated = await self.chart_repo.update(existing, update_data)
        return ChartResponse.model_validate(updated)

    async def delete(self, chart_id: int) -> None:
        chart = await self._get_chart(chart_id)
        await self.chart_repo.delete(chart)

    async def get_data(self, payload: ChartDataRequest) -> ChartDataResponse:
        chart = await self._get_optional_chart(payload.id)
        fields_source = payload.view_fields
        if fields_source is None and chart is not None:
            fields_source = chart.view_fields
        if fields_source is None:
            fields_source = self._merge_axis_fields(payload)
        normalized_fields = list(fields_source) if isinstance(fields_source, list) else []
        return ChartDataResponse(
            fields=normalized_fields,
            data=[],
            total=0,
            chart_id=chart.id if chart else payload.id,
            scene_id=chart.scene_id if chart else payload.scene_id,
        )

    async def get_detail(self, chart_id: int) -> ChartDetailResponse:
        chart = await self._get_chart(chart_id)
        fields = []
        if chart.table_id is not None:
            fields = [ChartFieldResponse.model_validate(item) for item in await self.field_repo.list_by_table(chart.table_id)]
        return ChartDetailResponse(chart=ChartResponse.model_validate(chart), fields=fields)

    async def view_detail_list(self, scene_id: int) -> list[ChartResponse]:
        charts = await self.chart_repo.list_by_scene(scene_id)
        return [ChartResponse.model_validate(chart) for chart in charts]

    async def _get_chart(self, chart_id: int) -> CoreChartView:
        chart = await self.chart_repo.get_by_id(chart_id)
        if chart is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
        return chart

    async def _get_optional_chart(self, chart_id: int | None) -> CoreChartView | None:
        if chart_id is None:
            return None
        return await self.chart_repo.get_by_id(chart_id)

    @staticmethod
    def _merge_axis_fields(payload: ChartDataRequest) -> list[object]:
        fields: list[object] = []
        for value in [payload.x_axis, payload.x_axis_ext, payload.y_axis, payload.y_axis_ext, payload.ext_bubble, payload.ext_label, payload.ext_stack, payload.ext_tooltip, payload.ext_color]:
            if isinstance(value, list):
                fields.extend(value)
        return fields


async def get_chart_service(session: AsyncSession = Depends(get_db)) -> ChartService:
    return ChartService(session)
