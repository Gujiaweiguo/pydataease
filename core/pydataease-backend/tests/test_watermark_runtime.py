from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select
from unittest.mock import Mock

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.models.sys_setting import CoreSysSetting  # pyright: ignore[reportImplicitRelativeImport]
from app.models.watermark import VisualizationWatermark  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.watermark_service import WatermarkService  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


def _auth_header(user_id: int = 7, oid: int = 9) -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=user_id, oid=oid)}


def _db_override(session):
    async def override_get_db() -> AsyncIterator[object]:
        yield session

    return override_get_db


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


async def _snapshot_watermark(session) -> VisualizationWatermark | None:
    return await session.get(VisualizationWatermark, "system_default")


async def _restore_watermark(session, snapshot: VisualizationWatermark | None) -> None:
    await session.execute(delete(VisualizationWatermark).where(VisualizationWatermark.id == "system_default"))
    await session.commit()
    if snapshot is not None:
        session.add(
            VisualizationWatermark(
                id=snapshot.id,
                version=snapshot.version,
                setting_content=snapshot.setting_content,
                create_by=snapshot.create_by,
                create_time=snapshot.create_time,
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_save_blocked_when_watermark_feature_disabled(
    client: AsyncClient,
    db_session,
) -> None:
    keys = ["feature.watermark.enabled"]
    snapshot = await _snapshot_settings(db_session, keys)
    app.dependency_overrides[get_db] = _db_override(db_session)
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        db_session.add(CoreSysSetting(setting_key="feature.watermark.enabled", setting_value="false", type="feature"))
        await db_session.commit()

        response = await client.post(
            "/de2api/watermark/save",
            json={"version": "1.0", "settingContent": '{"enable": true}'},
            headers=_auth_header(),
        )

        assert response.status_code == 403
        assert response.json() == {"code": 403, "data": None, "msg": "feature_disabled"}
    finally:
        _ = app.dependency_overrides.pop(get_db, None)
        _ = app.dependency_overrides.pop(get_current_user, None)
        await _restore_settings(db_session, snapshot, keys)


@pytest.mark.asyncio
async def test_public_endpoint_returns_disabled_when_no_config_exists(client: AsyncClient, db_session) -> None:
    keys = ["feature.watermark.enabled"]
    settings_snapshot = await _snapshot_settings(db_session, keys)
    watermark_snapshot = await _snapshot_watermark(db_session)
    app.dependency_overrides[get_db] = _db_override(db_session)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.execute(delete(VisualizationWatermark).where(VisualizationWatermark.id == "system_default"))
        await db_session.commit()

        response = await client.get("/de2api/watermark/public")

        assert response.status_code == 200
        assert response.json()["data"] == {"enable": False}
    finally:
        _ = app.dependency_overrides.pop(get_db, None)
        await _restore_settings(db_session, settings_snapshot, keys)
        await _restore_watermark(db_session, watermark_snapshot)


@pytest.mark.asyncio
async def test_public_endpoint_returns_disabled_when_feature_flag_off(client: AsyncClient, db_session) -> None:
    keys = ["feature.watermark.enabled"]
    settings_snapshot = await _snapshot_settings(db_session, keys)
    watermark_snapshot = await _snapshot_watermark(db_session)
    app.dependency_overrides[get_db] = _db_override(db_session)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.execute(delete(VisualizationWatermark).where(VisualizationWatermark.id == "system_default"))
        db_session.add(CoreSysSetting(setting_key="feature.watermark.enabled", setting_value="false", type="feature"))
        db_session.add(
            VisualizationWatermark(
                id="system_default",
                version="1.0",
                setting_content='{"enable": true, "text": "${username}", "opacity": 0.3, "fontSize": 14, "color": "#000000"}',
                create_by="tester",
                create_time=1,
            )
        )
        await db_session.commit()

        response = await client.get("/de2api/watermark/public")

        assert response.status_code == 200
        assert response.json()["data"] == {"enable": False}
    finally:
        _ = app.dependency_overrides.pop(get_db, None)
        await _restore_settings(db_session, settings_snapshot, keys)
        await _restore_watermark(db_session, watermark_snapshot)


@pytest.mark.asyncio
async def test_public_endpoint_returns_watermark_fields_when_enabled(client: AsyncClient, db_session) -> None:
    keys = ["feature.watermark.enabled"]
    settings_snapshot = await _snapshot_settings(db_session, keys)
    watermark_snapshot = await _snapshot_watermark(db_session)
    app.dependency_overrides[get_db] = _db_override(db_session)
    try:
        await db_session.execute(delete(CoreSysSetting).where(CoreSysSetting.setting_key.in_(keys)))
        await db_session.execute(delete(VisualizationWatermark).where(VisualizationWatermark.id == "system_default"))
        db_session.add(CoreSysSetting(setting_key="feature.watermark.enabled", setting_value="true", type="feature"))
        db_session.add(
            VisualizationWatermark(
                id="system_default",
                version="1.0",
                setting_content='{"enable": true, "text": "${username}", "opacity": 0.3, "fontSize": 14, "color": "#000000"}',
                create_by="tester",
                create_time=1,
            )
        )
        await db_session.commit()

        response = await client.get("/de2api/watermark/public")

        assert response.status_code == 200
        assert response.json()["data"] == {
            "enable": True,
            "text": "${username}",
            "opacity": 0.3,
            "fontSize": 14,
            "color": "#000000",
        }
    finally:
        _ = app.dependency_overrides.pop(get_db, None)
        await _restore_settings(db_session, settings_snapshot, keys)
        await _restore_watermark(db_session, watermark_snapshot)


@pytest.mark.asyncio
async def test_resolve_placeholders_replaces_known_and_unknown_values(db_session) -> None:
    service = WatermarkService(db_session)

    result = service.resolve_placeholders(
        "User:${username};Org:${orgName};Missing:${missing}",
        {"username": "alice", "orgName": "Acme"},
    )

    assert result == "User:alice;Org:Acme;Missing:"


@pytest.mark.asyncio
async def test_resolve_placeholders_uses_param_resolver_when_supplied(db_session) -> None:
    service = WatermarkService(db_session)
    resolver = Mock()
    resolver.resolve.return_value = (
        {
            "username": type("Resolved", (), {"value": "resolver-alice"})(),
            "orgName": type("Resolved", (), {"value": "Acme"})(),
            "missing": type("Resolved", (), {"value": None})(),
        },
        [],
    )

    result = service.resolve_placeholders(
        "User:${username};Org:${orgName};Missing:${missing}",
        {"username": "embed-alice", "orgName": "Acme"},
        resolver,
    )

    assert result == "User:resolver-alice;Org:Acme;Missing:"
    resolver.resolve.assert_called_once()


@pytest.mark.asyncio
async def test_resolve_watermark_text_uses_embed_context_resolution(db_session) -> None:
    service = WatermarkService(db_session)

    result = service.resolve_watermark_text(
        "User:${username};Org:${orgName};Missing:${missing}",
        {"username": "embed-alice", "orgName": "Acme"},
    )

    assert result == "User:embed-alice;Org:Acme;Missing:"
