from __future__ import annotations

from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.services.sys_setting_service import SysSettingService


@final
class TemplateMarketService:
    def __init__(self, session: AsyncSession) -> None:
        self.settings = SysSettingService(session)

    async def _get_base_url(self) -> str:
        try:
            url = await self.settings.get_setting("template.url")
        except Exception:
            url = None
        return url or ""

    async def search_recommend(self) -> dict[str, object]:
        base_url = await self._get_base_url()
        return {
            "baseUrl": base_url,
            "contents": [],
        }

    async def search(self) -> dict[str, object]:
        base_url = await self._get_base_url()
        return {
            "baseUrl": base_url,
            "categories": [],
            "contents": [],
        }

    async def search_preview(self) -> dict[str, object]:
        base_url = await self._get_base_url()
        return {
            "baseUrl": base_url,
            "categories": [],
            "contents": [],
        }

    async def get_categories(self) -> list[str]:
        return []

    async def get_categories_object(self) -> list[dict[str, str]]:
        return [
            {"value": "recent", "label": "最近", "source": "public"},
            {"value": "suggest", "label": "推荐", "source": "public"},
        ]


async def get_template_market_service(session: AsyncSession = Depends(get_db)) -> TemplateMarketService:
    return TemplateMarketService(session)
