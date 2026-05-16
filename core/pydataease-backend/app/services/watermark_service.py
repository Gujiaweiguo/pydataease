from __future__ import annotations

from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.watermark_repo import WatermarkRepository
from app.schemas.watermark import WatermarkResponse, WatermarkSaveRequest


@final
class WatermarkService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = WatermarkRepository(session)

    async def get_watermark_info(self) -> WatermarkResponse | None:
        entity = await self.repo.get()
        if entity is None:
            return None
        return WatermarkResponse.model_validate(entity)

    async def save_watermark_info(self, payload: WatermarkSaveRequest) -> None:
        update_data: dict[str, object] = {}
        if payload.version is not None:
            update_data["version"] = payload.version
        if payload.setting_content is not None:
            update_data["setting_content"] = payload.setting_content
        if update_data:
            await self.repo.update(update_data)


async def get_watermark_service(session: AsyncSession = Depends(get_db)) -> WatermarkService:
    return WatermarkService(session)
