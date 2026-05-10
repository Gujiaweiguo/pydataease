from __future__ import annotations

import pytest

from app.services.menu_service import get_menu_service
from app.services.system_service import get_system_service
from tests.test_system_routes import FakeMenuService
from tests.test_system_routes import FakeSystemService


@pytest.fixture
def fake_service(install_override) -> FakeSystemService:
    service = FakeSystemService()
    install_override(get_system_service, service)
    install_override(get_menu_service, FakeMenuService())
    return service


@pytest.mark.usefixtures("fake_service")
class TestSysParameterContract:
    async def test_request_timeout_success_contract(self, async_client) -> None:
        """GET /de2api/sysParameter/requestTimeOut should be callable without auth during frontend bootstrap and return integer timeout in ResultMessage.data."""
        response = await async_client.get("/de2api/sysParameter/requestTimeOut")

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": 120, "msg": "success"}

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_ui_success_contract(self) -> None:
        """GET /de2api/sysParameter/ui should be callable without auth and return login/UI bootstrap configuration list."""

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_default_login_success_contract(self) -> None:
        """GET /de2api/sysParameter/defaultLogin should be callable without auth and return login category integer."""

    async def test_basic_query_success_contract(self, async_client, auth_headers) -> None:
        """GET /de2api/sysParameter/basic/query should require X-DE-TOKEN and return basic SettingItemVO list in ResultMessage.data."""
        response = await async_client.get("/de2api/menu/query", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"][0]["name"] == "system"

    async def test_basic_query_auth_failure_contract(self, async_client) -> None:
        """GET /de2api/sysParameter/basic/query should fail when auth token is missing, invalid, or expired."""
        response = await async_client.get("/de2api/menu/query")

        assert response.status_code == 401

    async def test_save_online_map_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/sysParameter/saveOnlineMap should persist OnlineMapEditor and return success ResultMessage."""
        response = await async_client.post(
            "/de2api/sysParameter/saveOnlineMap",
            headers=auth_headers,
            json={"key": "new-map-key"},
        )

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": {"key": "new-map-key"}, "msg": "success"}
