from __future__ import annotations

from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.visualization_background import VisualizationBackground
from app.repositories.visualization_bg_repo import VisualizationBackgroundRepository


@final
class VisualizationBackgroundService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = VisualizationBackgroundRepository(session)

    async def find_all_grouped(self) -> dict[str, list[dict]]:
        """Return backgrounds grouped by classification field."""
        rows: list[VisualizationBackground] = await self.repo.list_all()
        grouped: dict[str, list[dict]] = {}
        for row in rows:
            cls_key = row.classification or "default"
            grouped.setdefault(cls_key, []).append(
                {
                    "id": row.id,
                    "name": row.name,
                    "classification": row.classification,
                    "content": row.content,
                    "remark": row.remark,
                    "sort": row.sort,
                    "uploadTime": row.upload_time,
                    "baseUrl": row.base_url,
                    "url": row.url,
                }
            )
        return grouped


async def get_bg_service(
    session: AsyncSession = Depends(get_db),
) -> VisualizationBackgroundService:
    return VisualizationBackgroundService(session)
