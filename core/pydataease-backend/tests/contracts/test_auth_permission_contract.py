from __future__ import annotations

from typing import Any

import pytest
from fastapi import HTTPException, status  # pyright: ignore[reportMissingImports]

from app.schemas.auth_permission import PermissionVO, ResourceVO  # pyright: ignore[reportImplicitRelativeImport]
from app.services.auth_permission_service import get_auth_permission_service  # pyright: ignore[reportImplicitRelativeImport]


class FakeAuthPermissionService:
    async def get_menu_resource_tree(self, user) -> list[ResourceVO]:
        del user
        return [ResourceVO(id="0", name="root", leaf=False, children=[])]

    async def get_busi_resource_tree(self, flag, user) -> list[ResourceVO]:
        del user
        if flag not in {"dashboard", "screen", "dataset", "datasource"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported resource flag")
        return [
            ResourceVO(
                id="0",
                name="root",
                leaf=False,
                children=[ResourceVO(id="100", name=f"test-{flag}", leaf=True)],
            )
        ]

    async def get_busi_permission(self, request, user) -> PermissionVO:
        del request, user
        return PermissionVO(root=True, readonly=False, permissions=[])

    async def get_menu_permission(self, request, user) -> PermissionVO:
        del request, user
        return PermissionVO(root=True, readonly=False, permissions=[])

    async def save_busi_per(self, editor, user) -> None:
        del editor, user

    async def save_menu_per(self, editor, user) -> None:
        del editor, user

    async def get_busi_target_permission(self, request, user) -> PermissionVO:
        del request, user
        return PermissionVO(root=False, readonly=True, permissions=[])

    async def get_menu_target_permission(self, request, user) -> PermissionVO:
        del request, user
        return PermissionVO(root=False, readonly=True, permissions=[])

    async def save_busi_target_per(self, creator, user) -> None:
        del creator, user

    async def save_menu_target_per(self, creator, user) -> None:
        del creator, user


@pytest.fixture
def fake_auth_permission_service(install_override) -> FakeAuthPermissionService:
    svc = FakeAuthPermissionService()
    install_override(get_auth_permission_service, svc)
    return svc


@pytest.mark.usefixtures("fake_auth_permission_service")
class TestAuthPermissionContract:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "url", "payload"),
        [
            ("GET", "/de2api/auth/menuResource", None),
            ("GET", "/de2api/auth/busiResource/dataset", None),
            ("POST", "/de2api/auth/busiPermission", {"id": 1, "type": 1, "flag": "dataset"}),
            ("POST", "/de2api/auth/menuPermission", {"id": 1}),
            ("POST", "/de2api/auth/saveBusiPer", {"id": 1, "type": 1, "flag": "dataset", "permissions": []}),
            ("POST", "/de2api/auth/saveMenuPer", {"id": 1, "permissions": []}),
            ("POST", "/de2api/auth/busiTargetPermission", {"id": 1, "type": 1, "flag": "dataset"}),
            ("POST", "/de2api/auth/menuTargetPermission", {"id": 1}),
            (
                "POST",
                "/de2api/auth/saveBusiTargetPer",
                {"ids": [1], "type": 1, "flag": "dataset", "permissions": []},
            ),
            ("POST", "/de2api/auth/saveMenuTargetPer", {"ids": [1], "permissions": []}),
        ],
    )
    async def test_all_auth_permission_endpoints_return_result_messages(
        self,
        async_client,
        auth_headers,
        method: str,
        url: str,
        payload: dict[str, Any] | None,
    ) -> None:
        if method == "GET":
            response = await async_client.get(url, headers=auth_headers)
        else:
            response = await async_client.post(url, headers=auth_headers, json=payload)

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert "data" in body
        assert body["msg"] == "success"

    @pytest.mark.asyncio
    async def test_busi_permission_contract_shape(self, async_client, auth_headers) -> None:
        response = await async_client.post(
            "/de2api/auth/busiPermission",
            headers=auth_headers,
            json={"id": 1, "type": 1, "flag": "dataset"},
        )

        body = response.json()
        assert body["code"] == 0
        assert body["data"]["root"] is True
        assert body["data"]["readonly"] is False
        assert body["data"]["permissions"] == []

    @pytest.mark.asyncio
    async def test_busi_resource_unsupported_flag_contract(self, async_client, auth_headers) -> None:
        response = await async_client.get("/de2api/auth/busiResource/invalid_flag", headers=auth_headers)

        assert response.status_code == 400
        assert response.json()["code"] == 400

    @pytest.mark.asyncio
    async def test_all_auth_permission_endpoints_require_authentication(self, async_client) -> None:
        endpoints = [
            ("GET", "/de2api/auth/menuResource", None),
            ("GET", "/de2api/auth/busiResource/dataset", None),
            ("POST", "/de2api/auth/busiPermission", {"id": 1, "type": 1, "flag": "dataset"}),
            ("POST", "/de2api/auth/menuPermission", {"id": 1}),
            ("POST", "/de2api/auth/saveBusiPer", {"id": 1, "type": 1, "flag": "dataset", "permissions": []}),
            ("POST", "/de2api/auth/saveMenuPer", {"id": 1, "permissions": []}),
            ("POST", "/de2api/auth/busiTargetPermission", {"id": 1, "type": 1, "flag": "dataset"}),
            ("POST", "/de2api/auth/menuTargetPermission", {"id": 1}),
            ("POST", "/de2api/auth/saveBusiTargetPer", {"ids": [1], "type": 1, "flag": "dataset", "permissions": []}),
            ("POST", "/de2api/auth/saveMenuTargetPer", {"ids": [1], "permissions": []}),
        ]

        for method, url, payload in endpoints:
            if method == "GET":
                response = await async_client.get(url)
            else:
                response = await async_client.post(url, json=payload)
            assert response.status_code == 401, f"{method} {url} should reject missing token"
            assert response.json()["code"] == 401
