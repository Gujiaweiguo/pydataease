"""Tests for MySQLBot API Key authentication dependency."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.main import app


# ---------------------------------------------------------------------------
# Fake setting repo — returns a known API key for sqlbot.apiKey
# ---------------------------------------------------------------------------

_FAKE_API_KEY = "test-secret-key-12345"


class _FakeSettingRow:
    def __init__(self, value: str) -> None:
        self.setting_value = value


class _FakeSysSettingRepo:
    def __init__(self, _session=None, *, stored_key: str = _FAKE_API_KEY) -> None:
        self._stored_key = stored_key

    async def get_by_key(self, key: str):
        if key == "sqlbot.apiKey" and self._stored_key:
            return _FakeSettingRow(self._stored_key)
        return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mysqlbot_missing_api_key_returns_401(client: AsyncClient) -> None:
    """Request without X-API-Key header should be rejected."""
    response = await client.get("/de2api/mysqlbot/api/datasources")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_mysqlbot_wrong_api_key_returns_401(client: AsyncClient) -> None:
    import app.dependencies.mysqlbot_auth as auth_mod

    original_repo = auth_mod.SysSettingRepository
    auth_mod.SysSettingRepository = _FakeSysSettingRepo
    try:
        response = await client.get(
            "/de2api/mysqlbot/api/datasources",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401
    finally:
        auth_mod.SysSettingRepository = original_repo


@pytest.mark.asyncio
async def test_mysqlbot_valid_api_key_passes_auth(client: AsyncClient) -> None:
    import app.dependencies.mysqlbot_auth as auth_mod
    from app.services.mysqlbot_service import MysqlBotService, get_mysqlbot_service

    original_repo = auth_mod.SysSettingRepository
    auth_mod.SysSettingRepository = _FakeSysSettingRepo

    class FakeService(MysqlBotService):
        def __init__(self) -> None:
            pass

        async def list_datasources(self):
            return []

    app.dependency_overrides[get_mysqlbot_service] = lambda: FakeService()
    try:
        response = await client.get(
            "/de2api/mysqlbot/api/datasources",
            headers={"X-API-Key": _FAKE_API_KEY},
        )
        assert response.status_code == 200
    finally:
        auth_mod.SysSettingRepository = original_repo
        app.dependency_overrides.pop(get_mysqlbot_service, None)


@pytest.mark.asyncio
async def test_mysqlbot_empty_stored_key_rejects_all(client: AsyncClient) -> None:
    import app.dependencies.mysqlbot_auth as auth_mod

    original_repo = auth_mod.SysSettingRepository
    auth_mod.SysSettingRepository = lambda session: _FakeSysSettingRepo(session, stored_key="")

    try:
        response = await client.get(
            "/de2api/mysqlbot/api/datasources",
            headers={"X-API-Key": "anything"},
        )
        assert response.status_code == 401
    finally:
        auth_mod.SysSettingRepository = original_repo
