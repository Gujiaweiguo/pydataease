"""Tests for user-role-extras routes."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def route_paths() -> set[str]:
    return {getattr(route, "path", "") for route in app.routes}


def api_path(path: str) -> str:
    return f"/de2api{path}"


class TestUserProfileRoutes:
    def test_user_info_route(self, route_paths):
        assert api_path("/user/info") in route_paths

    def test_person_info_route(self, route_paths):
        assert api_path("/user/personInfo") in route_paths

    def test_person_edit_route(self, route_paths):
        assert api_path("/user/personEdit") in route_paths

    def test_switch_org_route(self, route_paths):
        assert api_path("/user/switch/{oid}") in route_paths

    def test_ip_info_route(self, route_paths):
        assert api_path("/user/ipInfo") in route_paths


class TestUserPreferenceRoutes:
    def test_switch_language_route(self, route_paths):
        assert api_path("/user/switchLanguage") in route_paths

    def test_person_sys_variable_route(self, route_paths):
        assert api_path("/user/personSysVariableInfo/{uid}") in route_paths


class TestUserBatchRoutes:
    def test_batch_del_route(self, route_paths):
        assert api_path("/user/batchDel") in route_paths

    def test_batch_import_route(self, route_paths):
        assert api_path("/user/batchImport") in route_paths

    def test_excel_template_route(self, route_paths):
        assert api_path("/user/excelTemplate") in route_paths

    def test_error_record_route(self, route_paths):
        assert api_path("/user/errorRecord/{key}") in route_paths

    def test_clear_error_record_route(self, route_paths):
        assert api_path("/user/clearErrorRecord/{key}") in route_paths


class TestRoleExtraRoutes:
    def test_before_unmount_info_route(self, route_paths):
        assert api_path("/role/beforeUnmountInfo") in route_paths

    def test_mount_external_user_route(self, route_paths):
        assert api_path("/role/mountExternalUser") in route_paths


class TestAuthRequired:
    @pytest.mark.asyncio
    async def test_user_info_requires_auth(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/de2api/user/info")
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_person_edit_requires_auth(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/de2api/user/personEdit", json={"name": "test"})
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_switch_language_requires_auth(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/de2api/user/switchLanguage", json={"language": "en"})
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_batch_del_requires_auth(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/de2api/user/batchDel", json={"ids": [1]})
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_before_unmount_info_requires_auth(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/de2api/role/beforeUnmountInfo", json={"roleId": 1})
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_mount_external_user_requires_auth(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/de2api/role/mountExternalUser", json={"roleId": 1, "accounts": []})
        assert r.status_code in (401, 403)
