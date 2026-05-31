from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import app.services.platform as platform_registry  # pyright: ignore[reportImplicitRelativeImport]
from fastapi.routing import APIRoute  # pyright: ignore[reportMissingImports]
from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.main import api_router, app  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform.base import PlatformUserInfo  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform.dingtalk_provider import DingTalkPlatformProvider  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform.lark_provider import LarkPlatformProvider, LarkSuitePlatformProvider  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform.wecom_provider import WeComPlatformProvider  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform_service import PLATFORM_ORIGIN_MAP, PlatformService  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


@pytest.fixture
def auth_override():
    app.dependency_overrides[get_current_user] = lambda: TokenUser(user_id=7, oid=9)
    yield
    _ = app.dependency_overrides.pop(get_current_user, None)


def test_platform_provider_registry_has_all_platforms() -> None:
    assert platform_registry.platform_providers == {
        "wecom": WeComPlatformProvider,
        "dingtalk": DingTalkPlatformProvider,
        "lark": LarkPlatformProvider,
        "larksuite": LarkSuitePlatformProvider,
    }
    assert PLATFORM_ORIGIN_MAP == {"wecom": 4, "dingtalk": 5, "lark": 6, "larksuite": 7}


@pytest.mark.parametrize(
    ("provider_cls", "valid_config", "missing_key"),
    [
        (WeComPlatformProvider, {"corpId": "corp", "agentId": "agent", "secret": "secret1234", "callbackDomain": "https://x"}, "corpId"),
        (DingTalkPlatformProvider, {"appId": "app", "appKey": "key", "appSecret": "secret1234", "callbackDomain": "https://x"}, "appId"),
        (LarkPlatformProvider, {"appId": "app", "appSecret": "secret1234", "callbackDomain": "https://x"}, "appId"),
    ],
)
def test_provider_config_validation(provider_cls, valid_config, missing_key) -> None:
    assert provider_cls(valid_config).validate_config(valid_config) == []
    invalid = dict(valid_config)
    invalid.pop(missing_key)
    assert provider_cls(invalid).validate_config(invalid)


def test_provider_instantiation() -> None:
    wecom_cls = platform_registry.get_platform_provider("wecom")
    larksuite_cls = platform_registry.get_platform_provider("larksuite")
    assert wecom_cls is WeComPlatformProvider
    assert larksuite_cls is LarkSuitePlatformProvider
    assert isinstance(wecom_cls({"corpId": "1", "agentId": "2", "secret": "12345678", "callbackDomain": "https://x"}), WeComPlatformProvider)


def test_platform_router_endpoints_exist() -> None:
    route_objects = [route for route in api_router.routes if isinstance(route, APIRoute)]
    routes = {(route.path, tuple(sorted(route.methods or set()))) for route in route_objects}
    assert ("/de2api/platform/{platform}/save", ("POST",)) in routes
    assert ("/de2api/platform/{platform}/config", ("GET",)) in routes
    assert ("/de2api/platform/{platform}/validate", ("POST",)) in routes
    assert ("/de2api/platform/{platform}/qrinfo", ("GET",)) in routes
    assert ("/de2api/platform/{platform}/token", ("POST",)) in routes
    assert ("/de2api/platform/{platform}/bind", ("POST",)) in routes
    assert ("/de2api/platform/{platform}/unbind", ("POST",)) in routes
    assert ("/de2api/platform/bindings", ("GET",)) in routes
    assert ("/de2api/login/platformLogin/{origin}", ("POST",)) in routes


@pytest.mark.asyncio
async def test_config_save_load_masks_secret(monkeypatch) -> None:
    saved: dict[str, str] = {}

    async def fake_upsert(_self, key: str, value: str, setting_type: str = "setting"):
        saved[key] = value
        return SimpleNamespace(setting_key=key, setting_value=value, type=setting_type)

    async def fake_list_by_prefix(_self, prefix: str):
        return [
            SimpleNamespace(setting_key=f"{prefix}corpId", setting_value="corp-id"),
            SimpleNamespace(setting_key=f"{prefix}secret", setting_value="secret1234"),
        ]

    monkeypatch.setattr(SysSettingRepository, "upsert", fake_upsert)
    monkeypatch.setattr(SysSettingRepository, "list_by_prefix", fake_list_by_prefix)

    service = PlatformService(AsyncMock())
    await service.save_platform_config("wecom", {"corpId": "corp-id", "secret": "secret1234"})
    result = await service.get_platform_config("wecom")

    assert saved == {"platform.wecom.corpId": "corp-id", "platform.wecom.secret": "secret1234"}
    assert result == {"corpId": "corp-id", "secret": "secr****1234"}


@pytest.mark.asyncio
async def test_handle_platform_login_with_mocked_callback(monkeypatch) -> None:
    session = AsyncMock()
    service = PlatformService(session)
    user = SimpleNamespace(id=101, oid=0, password="hashed", enable=True)
    provider = AsyncMock()
    provider.handle_callback.return_value = PlatformUserInfo(
        platform="wecom",
        external_id="ext-1",
        username="alice",
        display_name="Alice",
        email="alice@example.com",
    )
    find_or_create = AsyncMock(return_value=user)
    create_or_update = AsyncMock()

    monkeypatch.setattr(service, "get_platform_config_raw", AsyncMock(return_value={"corpId": "corp"}))
    monkeypatch.setattr(service, "_build_provider", lambda platform, config: provider)
    monkeypatch.setattr(service, "_find_or_create_user", find_or_create)
    monkeypatch.setattr(service, "_create_or_update_link", create_or_update)

    auth_service = SimpleNamespace(
        _resolve_current_org_id=AsyncMock(return_value=9),
        _issue_token=lambda user_id, oid, password: SimpleNamespace(token="jwt-token", exp=123456),
    )
    monkeypatch.setattr("app.services.platform_service.AuthService", lambda s: auth_service)

    result = await service.handle_platform_login("wecom", "code-1", "state-1", "https://cb")

    provider.handle_callback.assert_awaited_once_with("code-1", "state-1", "https://cb")
    find_or_create.assert_awaited_once()
    create_or_update.assert_awaited_once()
    session.commit.assert_awaited_once()
    assert result == {"token": "jwt-token", "exp": 123456}


@pytest.mark.asyncio
async def test_platform_routes_use_service(client, auth_override, monkeypatch) -> None:
    _ = auth_override
    headers = {"X-DE-TOKEN": _build_token(uid=7, oid=9)}
    fake_service = AsyncMock()
    fake_service.get_platform_config.return_value = {"corpId": "corp", "secret": "****"}
    fake_service.validate_platform.return_value = {"success": True, "message": "ok"}
    fake_service.get_qr_url.return_value = "https://auth.example"
    fake_service.handle_platform_login.return_value = {"token": "jwt-token", "exp": 123}
    fake_service.get_platform_bindings.return_value = [{"platform": "wecom", "externalId": "ext-1", "origin": 4}]
    fake_service.get_platform_config_raw.return_value = {"callbackDomain": "https://cb.example"}

    monkeypatch.setattr("app.routers.platform.is_feature_enabled", AsyncMock(return_value=True))
    monkeypatch.setattr("app.routers.platform.PlatformService", lambda session: fake_service)

    response = await client.post("/de2api/platform/wecom/save", json={"config": {"corpId": "corp"}}, headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}

    response = await client.get("/de2api/platform/wecom/config", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"corpId": "corp", "secret": "****"}

    response = await client.post("/de2api/platform/wecom/validate", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"success": True, "message": "ok"}

    response = await client.get("/de2api/platform/wecom/qrinfo?redirect_uri=https://cb&state=s1")
    assert response.status_code == 200
    assert response.json()["data"] == {"authorizeUrl": "https://auth.example"}

    response = await client.post("/de2api/platform/wecom/token", json={"code": "c1", "state": "s1", "redirect_uri": "https://cb"})
    assert response.status_code == 200
    assert response.json()["data"] == {"token": "jwt-token", "exp": 123}

    response = await client.post("/de2api/login/platformLogin/wecom", json={"code": "c1", "state": "s1", "redirect_uri": "https://cb"})
    assert response.status_code == 200
    assert response.json()["data"] == {"token": "jwt-token", "exp": 123}

    response = await client.post("/de2api/platform/wecom/bind", json={"code": "c1", "state": "s1"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}

    response = await client.post("/de2api/platform/wecom/unbind", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}

    response = await client.get("/de2api/platform/bindings", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == [{"platform": "wecom", "externalId": "ext-1", "origin": 4}]
