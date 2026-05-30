from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select

# pyright: reportMissingImports=false

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.models.sys_setting import CoreSysSetting  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sys_setting_service import SysSettingService, get_sys_setting_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.system_service import SystemService  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import SETTINGS_DEFAULTS, get_default  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.seed import seed_defaults  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakePersistentSysSettingService:
    def __init__(self) -> None:
        self.values = {
            "sqlbot.id": "",
            "sqlbot.domain": "",
            "sqlbot.enabled": "false",
            "sqlbot.valid": "false",
            "login.authProviders": "[]",
        }

    async def get_setting(self, key: str) -> str | None:
        return self.values.get(key)

    async def get_sqlbot_settings(self) -> dict[str, str | bool | int | None]:
        return {
            "id": None if not self.values["sqlbot.id"] else int(self.values["sqlbot.id"]),
            "domain": self.values["sqlbot.domain"],
            "enabled": self.values["sqlbot.enabled"] == "true",
            "valid": self.values["sqlbot.valid"] == "true",
        }

    async def save_sqlbot_settings(self, payload: dict[str, Any]) -> dict[str, str | bool | int | None]:
        self.values["sqlbot.id"] = "" if payload.get("id") is None else str(payload.get("id"))
        self.values["sqlbot.domain"] = str(payload.get("domain", ""))
        self.values["sqlbot.enabled"] = "true" if payload.get("enabled", False) else "false"
        self.values["sqlbot.valid"] = "true" if payload.get("valid", False) else "false"
        return {
            "id": None if payload.get("id") is None else int(payload["id"]),
            "domain": str(payload.get("domain", "")),
            "enabled": bool(payload.get("enabled", False)),
            "valid": bool(payload.get("valid", False)),
        }


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_sys_setting_service() -> Generator[FakePersistentSysSettingService, None, None]:
    svc = FakePersistentSysSettingService()
    app.dependency_overrides[get_sys_setting_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_sys_setting_service, None)


async def _snapshot_settings(session, keys: list[str]) -> dict[str, tuple[str | None, str | None]]:
    result = await session.execute(select(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
    rows = result.scalars().all()
    return {row.setting_key: (row.setting_value, row.type) for row in rows}


async def _restore_settings(session, snapshot: dict[str, tuple[str | None, str | None]], keys: list[str]) -> None:
    await session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
    await session.commit()
    for key, (value, setting_type) in snapshot.items():
        session.add(CoreSysSetting(setting_key=key, setting_value=value, type=setting_type))
    await session.commit()


@pytest.mark.asyncio
async def test_settings_defaults_contains_expected_keys() -> None:
    assert SETTINGS_DEFAULTS == {
        "map.onlineMapType": "gaode",
        "map.defaultMapType": "gaode",
        "map.gaode.key": "",
        "map.gaode.securityCode": "",
        "ui.themeColor": "",
        "ui.navigationBarStyle": "default",
        "ui.loginTitle": "",
        "ui.loginSubtitle": "",
        "ui.footerText": "",
        "ui.footerLink": "",
        "ui.helpLink": "",
        "ui.demoPromptEnabled": "false",
        "ui.demoPromptText": "",
        "ui.demoPromptLink": "",
        "ui.fontFallbackStack": "PingFang, sans-serif",
        "ui.cacheVersion": "0",
        "ui.updatedAt": "0",
        "basic.siteName": "PyDataEase",
        "engine.requestTimeOut": "120",
        "sqlbot.id": "",
        "sqlbot.domain": "",
        "sqlbot.enabled": "false",
        "sqlbot.valid": "false",
        "login.authProviders": "[]",
        "login.defaultMethod": "0",
        "share.disable": "true",
        "share.peRequire": "false",
        "defaultSettings.sort": "asc",
        "i18n.options": "{}",
    }


@pytest.mark.asyncio
async def test_get_default_returns_value_or_none() -> None:
    assert get_default("engine.requestTimeOut") == "120"
    assert get_default("missing.setting") is None


@pytest.mark.asyncio
async def test_seed_defaults_inserts_missing_rows_and_is_idempotent(db_session) -> None:
    keys = list(SETTINGS_DEFAULTS)
    snapshot = await _snapshot_settings(db_session, keys)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.commit()
        db_session.add(CoreSysSetting(setting_key="engine.requestTimeOut", setting_value="321", type="engine"))
        await db_session.commit()

        await seed_defaults()
        await seed_defaults()

        result = await db_session.execute(select(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        rows = result.scalars().all()
        values = {row.setting_key: row.setting_value for row in rows}
        types = {row.setting_key: row.type for row in rows}

        assert len(rows) == len(keys)
        assert values["engine.requestTimeOut"] == "321"
        assert values["map.onlineMapType"] == "gaode"
        assert types["sqlbot.valid"] == "sqlbot"
        assert types["i18n.options"] == "i18n"
    finally:
        await _restore_settings(db_session, snapshot, keys)


@pytest.mark.asyncio
async def test_online_map_persistence_roundtrip(db_session) -> None:
    keys = [
        "map.onlineMapType",
        "map.defaultMapType",
        "map.gaode.key",
        "map.gaode.securityCode",
        "map.qq.key",
        "map.qq.securityCode",
    ]
    snapshot = await _snapshot_settings(db_session, keys)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.commit()
        service = SystemService(db_session)
        await service.save_online_map("qq-key", "qq", "qq-sec")

        active_map = await service.query_online_map()
        qq_map = await service.query_online_map_by_type("qq")
        gaode_map = await service.query_online_map_by_type("gaode")

        assert active_map.model_dump(by_alias=True) == {"key": "qq-key", "mapType": "qq", "securityCode": "qq-sec"}
        assert qq_map.model_dump(by_alias=True) == {"key": "qq-key", "mapType": "qq", "securityCode": "qq-sec"}
        assert gaode_map.model_dump(by_alias=True) == {"key": "", "mapType": "gaode", "securityCode": ""}
    finally:
        await _restore_settings(db_session, snapshot, keys)


@pytest.mark.asyncio
async def test_request_timeout_persistence(db_session) -> None:
    keys = ["engine.requestTimeOut"]
    snapshot = await _snapshot_settings(db_session, keys)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key == "engine.requestTimeOut"))
        await db_session.commit()
        service = SystemService(db_session)
        assert await service.request_timeout() == 120

        setting_service = SysSettingService(db_session)
        await setting_service.upsert_setting("engine.requestTimeOut", "456", "engine")
        assert await service.request_timeout() == 456
    finally:
        await _restore_settings(db_session, snapshot, keys)


@pytest.mark.asyncio
async def test_sqlbot_get_post_persistence(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_sys_setting_service: FakePersistentSysSettingService,
) -> None:
    response = await client.get("/de2api/sysParameter/sqlbot")
    assert response.status_code == 200
    assert response.json()["data"] == {"id": None, "domain": "", "enabled": False, "valid": False}

    payload = {"id": 12, "domain": "https://sqlbot.local", "enabled": True, "valid": True}
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    try:
        save_response = await client.post("/de2api/sysParameter/sqlbot", json=payload, headers=auth_headers)
        assert save_response.status_code == 200
        assert save_response.json()["data"] == payload

        reread_response = await client.get("/de2api/sysParameter/sqlbot")
        assert reread_response.status_code == 200
        assert reread_response.json()["data"] == payload
    finally:
        _ = app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_sqlbot_post_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/sysParameter/sqlbot", json={"domain": "x"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_status_persistence(
    client: AsyncClient,
    fake_sys_setting_service: FakePersistentSysSettingService,
) -> None:
    fake_sys_setting_service.values["login.authProviders"] = json.dumps([
        {"type": "ldap", "enabled": True},
        {"type": "oidc", "enabled": False},
    ])

    response = await client.get("/de2api/setting/authentication/status")
    assert response.status_code == 200
    assert response.json()["data"] == [
        {"type": "ldap", "enabled": True},
        {"type": "oidc", "enabled": False},
    ]


@pytest.mark.asyncio
async def test_default_login_compatibility_alias(db_session) -> None:
    keys = ["login.defaultMethod", "defaultLogin"]
    snapshot = await _snapshot_settings(db_session, keys)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.commit()
        service = SysSettingService(db_session)
        assert await service.get_default_login() == 0

        await service.upsert_setting("defaultLogin", "1", "login")
        assert await service.get_default_login() == 1

        await service.upsert_setting("login.defaultMethod", "2", "login")
        assert await service.get_default_login() == 2
    finally:
        await _restore_settings(db_session, snapshot, keys)
