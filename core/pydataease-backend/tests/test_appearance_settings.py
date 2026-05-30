from __future__ import annotations

from collections.abc import Generator

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.models.sys_setting import CoreSysSetting  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sys_setting_service import SysSettingService, get_sys_setting_service  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import SETTINGS_DEFAULTS  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]

APPEARANCE_KEYS = [key for key in SETTINGS_DEFAULTS if key.startswith("ui.")]
APPEARANCE_KEYS_WITH_SITE = [*APPEARANCE_KEYS, "basic.siteName"]


class FakeAppearanceSettingService:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get_setting(self, key: str) -> str | None:
        return self.values.get(key)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_appearance_service() -> Generator[FakeAppearanceSettingService, None, None]:
    svc = FakeAppearanceSettingService()
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
async def test_appearance_defaults_contain_expected_keys() -> None:
    assert SETTINGS_DEFAULTS["ui.themeColor"] == ""
    assert SETTINGS_DEFAULTS["ui.navigationBarStyle"] == "default"
    assert SETTINGS_DEFAULTS["ui.loginTitle"] == ""
    assert SETTINGS_DEFAULTS["ui.loginSubtitle"] == ""
    assert SETTINGS_DEFAULTS["ui.footerText"] == ""
    assert SETTINGS_DEFAULTS["ui.footerLink"] == ""
    assert SETTINGS_DEFAULTS["ui.helpLink"] == ""
    assert SETTINGS_DEFAULTS["ui.demoPromptEnabled"] == "false"
    assert SETTINGS_DEFAULTS["ui.demoPromptText"] == ""
    assert SETTINGS_DEFAULTS["ui.demoPromptLink"] == ""
    assert SETTINGS_DEFAULTS["ui.fontFallbackStack"] == "PingFang, sans-serif"
    assert SETTINGS_DEFAULTS["ui.cacheVersion"] == "0"
    assert SETTINGS_DEFAULTS["ui.updatedAt"] == "0"
    assert SETTINGS_DEFAULTS["basic.siteName"] == "PyDataEase"


@pytest.mark.asyncio
async def test_public_read_returns_all_appearance_keys_with_defaults(
    client: AsyncClient,
    fake_appearance_service: FakeAppearanceSettingService,
) -> None:
    _ = fake_appearance_service
    response = await client.get("/de2api/sysParameter/appearance")

    assert response.status_code == 200
    assert response.json()["data"] == {key: SETTINGS_DEFAULTS[key] for key in APPEARANCE_KEYS_WITH_SITE}


@pytest.mark.asyncio
async def test_admin_save_persists_values_and_increments_cache_version(
    client: AsyncClient,
    db_session,
    auth_headers: dict[str, str],
) -> None:
    keys = [*APPEARANCE_KEYS_WITH_SITE, "feature.appearance.enabled"]
    snapshot = await _snapshot_settings(db_session, keys)
    app.dependency_overrides[get_sys_setting_service] = lambda: SysSettingService(db_session)
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.commit()

        payload = [
            {"pkey": "ui.themeColor", "pval": "#1890ff"},
            {"pkey": "ui.loginTitle", "pval": "Hello"},
            {"pkey": "basic.siteName", "pval": "Brand X"},
        ]
        response = await client.post("/de2api/sysParameter/appearance/save", json=payload, headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["data"] == {"status": "ok"}

        result = await db_session.execute(select(CoreSysSetting).where(CoreSysSetting.setting_key.in_(APPEARANCE_KEYS_WITH_SITE)))
        rows = {row.setting_key: row for row in result.scalars().all()}
        assert rows["ui.themeColor"].setting_value == "#1890ff"
        assert rows["ui.themeColor"].type == "ui"
        assert rows["ui.loginTitle"].setting_value == "Hello"
        assert rows["basic.siteName"].setting_value == "Brand X"
        assert rows["basic.siteName"].type == "basic"
        assert rows["ui.cacheVersion"].setting_value == "1"
        assert rows["ui.updatedAt"].setting_value is not None
        assert int(rows["ui.updatedAt"].setting_value or "0") > 0
    finally:
        _ = app.dependency_overrides.pop(get_sys_setting_service, None)
        _ = app.dependency_overrides.pop(get_current_user, None)
        await _restore_settings(db_session, snapshot, keys)


@pytest.mark.asyncio
async def test_admin_save_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/sysParameter/appearance/save",
        json=[{"pkey": "ui.themeColor", "pval": "#1890ff"}],
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_save_rejects_non_ui_keys(
    client: AsyncClient,
    db_session,
    auth_headers: dict[str, str],
) -> None:
    keys = ["feature.appearance.enabled"]
    snapshot = await _snapshot_settings(db_session, keys)
    app.dependency_overrides[get_sys_setting_service] = lambda: SysSettingService(db_session)
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    try:
        response = await client.post(
            "/de2api/sysParameter/appearance/save",
            json=[{"pkey": "engine.requestTimeOut", "pval": "999"}],
            headers=auth_headers,
        )
        assert response.status_code == 400
    finally:
        _ = app.dependency_overrides.pop(get_sys_setting_service, None)
        _ = app.dependency_overrides.pop(get_current_user, None)
        await _restore_settings(db_session, snapshot, keys)


@pytest.mark.asyncio
async def test_feature_flag_disabled_blocks_save(
    client: AsyncClient,
    db_session,
    auth_headers: dict[str, str],
) -> None:
    keys = ["feature.appearance.enabled", *APPEARANCE_KEYS_WITH_SITE]
    snapshot = await _snapshot_settings(db_session, keys)
    app.dependency_overrides[get_sys_setting_service] = lambda: SysSettingService(db_session)
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.commit()
        db_session.add(CoreSysSetting(setting_key="feature.appearance.enabled", setting_value="false", type="feature"))
        await db_session.commit()

        response = await client.post(
            "/de2api/sysParameter/appearance/save",
            json=[{"pkey": "ui.themeColor", "pval": "#1890ff"}],
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert response.json() == {"code": 1, "data": None, "msg": "feature_disabled"}
    finally:
        _ = app.dependency_overrides.pop(get_sys_setting_service, None)
        _ = app.dependency_overrides.pop(get_current_user, None)
        await _restore_settings(db_session, snapshot, keys)


@pytest.mark.asyncio
async def test_feature_flag_disabled_returns_defaults_on_read(
    client: AsyncClient,
    fake_appearance_service: FakeAppearanceSettingService,
) -> None:
    fake_appearance_service.values["feature.appearance.enabled"] = "false"

    response = await client.get("/de2api/sysParameter/appearance")

    assert response.status_code == 200
    assert response.json()["data"] == {key: SETTINGS_DEFAULTS[key] for key in APPEARANCE_KEYS_WITH_SITE}
