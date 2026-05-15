from __future__ import annotations

import json
from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.sys_setting_repo import SysSettingRepository


@final
class SysSettingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = SysSettingRepository(session)

    async def get_ui_settings(self) -> list[dict] | dict:
        """Return UI settings as list of {key, value} dicts (frontend expects array)."""
        try:
            rows = await self.repo.list_by_type("ui")
        except (AttributeError, TypeError):
            return {}
        return [{"key": row.setting_key, "value": row.setting_value or ""} for row in rows]

    async def get_setting(self, key: str) -> str | None:
        try:
            row = await self.repo.get_by_key(key)
        except (AttributeError, TypeError):
            return None
        return row.setting_value if row else None

    async def get_default_settings(self) -> dict:
        try:
            value = await self.get_setting("defaultSettings.sort")
        except (AttributeError, TypeError):
            return {}
        return {"sort": value or "asc"}

    async def get_i18n_options(self) -> dict:
        try:
            value = await self.get_setting("i18nOptions")
            if value:
                return json.loads(value)
        except (AttributeError, TypeError, json.JSONDecodeError):
            pass
        return {}

    async def get_share_base(self) -> dict:
        try:
            disable = await self.get_setting("shareBase.disable")
            pe_require = await self.get_setting("shareBase.peRequire")
        except (AttributeError, TypeError):
            return {"disable": True, "peRequire": False}
        return {
            "disable": disable != "false",
            "peRequire": pe_require == "true",
        }

    async def get_default_login(self) -> int:
        try:
            value = await self.get_setting("defaultLogin")
        except (AttributeError, TypeError):
            return 0
        return int(value) if value else 0


async def get_sys_setting_service(session: AsyncSession = Depends(get_db)) -> SysSettingService:
    return SysSettingService(session)
