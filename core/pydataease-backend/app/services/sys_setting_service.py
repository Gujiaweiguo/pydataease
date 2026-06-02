from __future__ import annotations

import json
import logging
from typing import Any, final

# pyright: reportMissingImports=false

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import get_default  # pyright: ignore[reportImplicitRelativeImport]

logger = logging.getLogger(__name__)


def _coerce_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        return None


@final
class SysSettingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = SysSettingRepository(session)

    async def get_ui_settings(self) -> list[dict[str, str]] | dict[str, str]:
        """Return UI settings as list of {key, value} dicts (frontend expects array)."""
        try:
            rows = await self.repo.list_by_type("ui")
        except (AttributeError, TypeError) as exc:
            logger.warning("SysSetting lookup failed for key 'ui': %s", exc)
            return {}
        return [{"key": row.setting_key, "value": row.setting_value or ""} for row in rows]

    async def get_setting(self, key: str) -> str | None:
        try:
            row = await self.repo.get_by_key(key)
        except (AttributeError, TypeError) as exc:
            logger.warning("SysSetting lookup failed for key '%s': %s", key, exc)
            return None
        return row.setting_value if row else None

    async def upsert_setting(self, key: str, value: str, setting_type: str | None = None) -> str:
        setting = await self.repo.upsert(key, value, setting_type or key.split(".", 1)[0])
        return setting.setting_value or ""

    async def get_default_settings(self) -> dict[str, str]:
        try:
            value = await self.get_setting("defaultSettings.sort")
        except (AttributeError, TypeError) as exc:
            logger.warning("SysSetting lookup failed: %s", exc)
            return {}
        return {"sort": value or get_default("defaultSettings.sort") or "asc"}

    async def get_i18n_options(self) -> dict[str, object]:
        try:
            value = await self.get_setting("i18n.options") or await self.get_setting("i18nOptions")
            if value:
                return json.loads(value)
        except (AttributeError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("SysSetting i18n lookup failed: %s", exc)
        default_value = get_default("i18n.options")
        return json.loads(default_value) if default_value else {}

    async def get_share_base(self) -> dict[str, bool]:
        try:
            disable = await self.get_setting("share.disable") or await self.get_setting("shareBase.disable")
            pe_require = await self.get_setting("share.peRequire") or await self.get_setting("shareBase.peRequire")
        except (AttributeError, TypeError) as exc:
            logger.warning("SysSetting shareBase lookup failed: %s", exc)
            return {"disable": True, "peRequire": False}
        return {
            "disable": (disable or get_default("share.disable") or "true") != "false",
            "peRequire": pe_require == "true",
        }

    async def get_default_login(self) -> int:
        try:
            value = await self.get_setting("login.defaultMethod")
            if value is None:
                value = await self.get_setting("defaultLogin")
        except (AttributeError, TypeError) as exc:
            logger.warning("SysSetting defaultLogin lookup failed: %s", exc)
            return 0
        return int(value) if value else int(get_default("login.defaultMethod") or 0)

    async def get_sqlbot_settings(self) -> dict[str, str | bool | int | None]:
        sqlbot_id = await self.get_setting("sqlbot.id")
        domain = await self.get_setting("sqlbot.domain")
        enabled = await self.get_setting("sqlbot.enabled")
        valid = await self.get_setting("sqlbot.valid")
        mode = await self.get_setting("sqlbot.mode")
        api_key = await self.get_setting("sqlbot.apiKey")
        aes_key = await self.get_setting("sqlbot.aesKey")
        aes_iv = await self.get_setting("sqlbot.aesIv")
        return {
            "id": _coerce_int(sqlbot_id),
            "domain": domain or get_default("sqlbot.domain") or "",
            "enabled": (enabled or get_default("sqlbot.enabled") or "false") == "true",
            "valid": (valid or get_default("sqlbot.valid") or "false") == "true",
            "mode": mode or get_default("sqlbot.mode") or "basic",
            "apiKey": api_key or "",
            "aesKey": aes_key or "",
            "aesIv": aes_iv or "",
        }

    async def save_sqlbot_settings(self, payload: dict[str, Any]) -> dict[str, str | bool | int | None]:
        sqlbot_id = payload.get("id")
        domain = payload.get("domain", "")
        enabled = bool(payload.get("enabled", False))
        valid = bool(payload.get("valid", False))
        mode = payload.get("mode", "basic")
        api_key = payload.get("apiKey", "")
        aes_key = payload.get("aesKey", "")
        aes_iv = payload.get("aesIv", "")
        await self.upsert_setting("sqlbot.id", "" if sqlbot_id is None else str(sqlbot_id), "sqlbot")
        await self.upsert_setting("sqlbot.domain", str(domain), "sqlbot")
        await self.upsert_setting("sqlbot.enabled", "true" if enabled else "false", "sqlbot")
        await self.upsert_setting("sqlbot.valid", "true" if valid else "false", "sqlbot")
        await self.upsert_setting("sqlbot.mode", str(mode), "sqlbot")
        await self.upsert_setting("sqlbot.apiKey", str(api_key), "sqlbot")
        await self.upsert_setting("sqlbot.aesKey", str(aes_key), "sqlbot")
        await self.upsert_setting("sqlbot.aesIv", str(aes_iv), "sqlbot")
        return {
            "id": sqlbot_id,
            "domain": str(domain),
            "enabled": enabled,
            "valid": valid,
            "mode": str(mode),
            "apiKey": str(api_key),
            "aesKey": str(aes_key),
            "aesIv": str(aes_iv),
        }


async def get_sys_setting_service(session: AsyncSession = Depends(get_db)) -> SysSettingService:
    return SysSettingService(session)
