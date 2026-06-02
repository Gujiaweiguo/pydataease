"""FastAPI dependency for MySQLBot advanced assistant API Key authentication."""

from __future__ import annotations

import hmac

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import get_default  # pyright: ignore[reportImplicitRelativeImport]


async def _get_stored_api_key(session: AsyncSession) -> str:
    """Retrieve the stored MySQLBot API Key from database or defaults."""
    row = await SysSettingRepository(session).get_by_key("sqlbot.apiKey")
    if row is not None and row.setting_value:
        return row.setting_value
    return get_default("sqlbot.apiKey") or ""


async def verify_mysqlbot_apikey(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> str:
    """Validate X-API-Key header against stored MySQLBot API Key.

    Uses constant-time comparison to prevent timing attacks.
    Returns the API key on success; raises HTTPException on failure.
    """
    api_key_header = request.headers.get("X-API-Key")

    if not api_key_header:
        raise HTTPException(status_code=401, detail="Missing API Key")

    stored_key = await _get_stored_api_key(session)

    if not stored_key or not hmac.compare_digest(api_key_header, stored_key):
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return api_key_header
