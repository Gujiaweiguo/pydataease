from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.models.sys_setting import CoreSysSetting  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sys_setting_service import get_sys_setting_service  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import SETTINGS_DEFAULTS, is_feature_enabled  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]

skip_no_db = pytest.mark.skipif(
    os.getenv("DE_E2E") != "1",
    reason="Requires PostgreSQL (set DE_E2E=1)",
)


FEATURE_KEYS = [key for key in SETTINGS_DEFAULTS if key.startswith("feature.")]


class FakeFeatureFlagService:
    def __init__(self) -> None:
        self.values = {key: value for key, value in SETTINGS_DEFAULTS.items() if key.startswith("feature.")}
        self.upserts: list[tuple[str, str, str | None]] = []

    async def get_setting(self, key: str) -> str | None:
        return self.values.get(key)

    async def upsert_setting(self, key: str, value: str, setting_type: str | None = None) -> str:
        self.values[key] = value
        self.upserts.append((key, value, setting_type))
        return value


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_feature_service() -> Generator[FakeFeatureFlagService, None, None]:
    svc = FakeFeatureFlagService()
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


@skip_no_db
@pytest.mark.asyncio
async def test_is_feature_enabled_returns_true_for_true_value(db_session) -> None:
    key = "feature.watermark.enabled"
    snapshot = await _snapshot_settings(db_session, [key])
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key == key))
        await db_session.commit()
        db_session.add(CoreSysSetting(setting_key=key, setting_value="true", type="feature"))
        await db_session.commit()

        assert await is_feature_enabled(db_session, key) is True
    finally:
        await _restore_settings(db_session, snapshot, [key])


@skip_no_db
@pytest.mark.asyncio
async def test_is_feature_enabled_returns_false_for_false_value(db_session) -> None:
    key = "feature.watermark.enabled"
    snapshot = await _snapshot_settings(db_session, [key])
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key == key))
        await db_session.commit()
        db_session.add(CoreSysSetting(setting_key=key, setting_value="false", type="feature"))
        await db_session.commit()

        assert await is_feature_enabled(db_session, key) is False
    finally:
        await _restore_settings(db_session, snapshot, [key])


@skip_no_db
@pytest.mark.asyncio
async def test_is_feature_enabled_falls_back_to_defaults_when_missing(db_session) -> None:
    key = "feature.embedding.enabled"
    snapshot = await _snapshot_settings(db_session, [key])
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key == key))
        await db_session.commit()

        assert await is_feature_enabled(db_session, key) is True
    finally:
        await _restore_settings(db_session, snapshot, [key])


@skip_no_db
@pytest.mark.asyncio
async def test_is_feature_enabled_returns_false_for_unknown_key(db_session) -> None:
    assert await is_feature_enabled(db_session, "feature.unknown.enabled") is False


@pytest.mark.asyncio
async def test_toggle_feature_flag_persists_and_returns_state(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_feature_service: FakeFeatureFlagService,
) -> None:
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    try:
        response = await client.post(
            "/de2api/sysParameter/feature/toggle",
            json={"key": "feature.watermark.enabled", "enabled": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["data"] == {"key": "feature.watermark.enabled", "enabled": True}
        assert fake_feature_service.values["feature.watermark.enabled"] == "true"
        assert fake_feature_service.upserts[-1] == ("feature.watermark.enabled", "true", "feature")
    finally:
        _ = app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_toggle_feature_flag_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/sysParameter/feature/toggle",
        json={"key": "feature.watermark.enabled", "enabled": True},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_toggle_feature_flag_rejects_non_feature_keys(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    try:
        response = await client.post(
            "/de2api/sysParameter/feature/toggle",
            json={"key": "sqlbot.enabled", "enabled": True},
            headers=auth_headers,
        )
        assert response.status_code == 400
    finally:
        _ = app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_feature_status_endpoint_returns_all_flags(
    client: AsyncClient,
    fake_feature_service: FakeFeatureFlagService,
) -> None:
    fake_feature_service.values["feature.dataFiling.enabled"] = "true"

    response = await client.get("/de2api/sysParameter/feature/status")

    assert response.status_code == 200
    assert response.json()["data"] == {
        "feature.adminConfig.enabled": True,
        "feature.appearance.enabled": True,
        "feature.watermark.enabled": True,
        "feature.sysVariableContract.enabled": True,
        "feature.embedding.enabled": True,
        "feature.platformIntegration.enabled": True,
        "feature.identification.enabled": False,
        "feature.dataFiling.enabled": True,
    }


@pytest.mark.asyncio
async def test_feature_status_endpoint_is_public(
    client: AsyncClient,
    fake_feature_service: FakeFeatureFlagService,
) -> None:
    fake_feature_service.values["feature.platformIntegration.enabled"] = "false"
    response = await client.get("/de2api/sysParameter/feature/status")

    assert response.status_code == 200
    assert set(response.json()["data"]) == set(FEATURE_KEYS)
    assert response.json()["data"]["feature.platformIntegration.enabled"] is False
