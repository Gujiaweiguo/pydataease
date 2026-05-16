from __future__ import annotations

from typing import final

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watermark import VisualizationWatermark

DEFAULT_ID = "system_default"


@final
class WatermarkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> VisualizationWatermark | None:
        return await self.session.get(VisualizationWatermark, DEFAULT_ID)

    async def update(self, payload: dict[str, object]) -> VisualizationWatermark:
        entity = await self.session.get(VisualizationWatermark, DEFAULT_ID)
        if entity is None:
            entity = VisualizationWatermark(id=DEFAULT_ID, **payload)
            self.session.add(entity)
        else:
            for key, value in payload.items():
                setattr(entity, key, value)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
