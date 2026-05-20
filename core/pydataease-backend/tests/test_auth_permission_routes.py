from __future__ import annotations

from collections.abc import AsyncGenerator
from types import MethodType, SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException, status  # pyright: ignore[reportMissingImports]
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.auth_permission_repo import AuthPermissionRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth_permission import (  # pyright: ignore[reportImplicitRelativeImport]
    BusiPermissionRequest,
    MenuPermissionRequest,
    PermissionItem,
    PermissionVO,
    ResourceVO,
)
from app.services.auth_permission_service import (  # pyright: ignore[reportImplicitRelativeImport]
    AuthPermissionService,
    get_auth_permission_service,
)
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]

AUTH_HEADERS = {"X-DE-TOKEN": _build_token(uid=1, oid=1)}
NON_ADMIN_HEADERS = {"X-DE-TOKEN": _build_token(uid=7, oid=9)}
INVALID_HEADERS = {"X-DE-TOKEN": "invalid-token-that-is-long-enough-to-pass-min-check"}


def _assert_result_message(body: dict[str, Any], *, code: int = 0) -> None:
    assert body["code"] == code
    assert "data" in body
    assert "msg" in body


class FakeAuthPermissionService:
    def __init__(self) -> None:
        self.saved_busi_per: dict[tuple[int, int, str], list[PermissionItem]] = {}
        self.saved_menu_per: dict[int, list[PermissionItem]] = {}
        self.saved_busi_target_per: dict[tuple[int, str, int], list[PermissionItem]] = {}
        self.saved_menu_target_per: dict[int, list[PermissionItem]] = {}

    async def get_menu_resource_tree(self, user) -> list[ResourceVO]:
        del user
        return [
            ResourceVO(
                id="0",
                name="root",
                leaf=False,
                children=[ResourceVO(id="1", name="dashboard-menu", leaf=True)],
            )
        ]

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
        del user
        permissions = self.saved_busi_per.get((request.type, request.id, request.flag), [])
        return PermissionVO(root=False, readonly=False, permissions=permissions)

    async def get_menu_permission(self, request, user) -> PermissionVO:
        del user
        return PermissionVO(root=False, readonly=False, permissions=self.saved_menu_per.get(request.id, []))

    async def save_busi_per(self, editor, user) -> None:
        del user
        self.saved_busi_per[(editor.type, editor.id, editor.flag)] = list(editor.permissions)

    async def save_menu_per(self, editor, user) -> None:
        del user
        self.saved_menu_per[editor.id] = list(editor.permissions)

    async def get_busi_target_permission(self, request, user) -> PermissionVO:
        del user
        permissions = self.saved_busi_target_per.get((request.type, request.flag, request.id), [])
        return PermissionVO(root=False, readonly=True, permissions=permissions)

    async def get_menu_target_permission(self, request, user) -> PermissionVO:
        del user
        return PermissionVO(root=False, readonly=True, permissions=self.saved_menu_target_per.get(request.id, []))

    async def save_busi_target_per(self, creator, user) -> None:
        del user
        for target_id in creator.ids:
            self.saved_busi_target_per[(creator.type, creator.flag, target_id)] = list(creator.permissions)

    async def save_menu_target_per(self, creator, user) -> None:
        del user
        for target_id in creator.ids:
            self.saved_menu_target_per[target_id] = list(creator.permissions)


@pytest.fixture
async def fake_service() -> AsyncGenerator[FakeAuthPermissionService, None]:
    svc = FakeAuthPermissionService()
    app.dependency_overrides[get_auth_permission_service] = lambda: svc
    yield svc
    app.dependency_overrides.pop(get_auth_permission_service, None)


@pytest.mark.usefixtures("fake_service")
class TestAuthRouteContract:
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
    async def test_auth_routes_are_wrapped(
        self,
        client: AsyncClient,
        method: str,
        url: str,
        payload: dict[str, Any] | None,
    ) -> None:
        if method == "GET":
            response = await client.get(url, headers=AUTH_HEADERS)
        else:
            response = await client.post(url, headers=AUTH_HEADERS, json=payload)

        assert response.status_code == 200
        body = response.json()
        _assert_result_message(body)
        assert body["msg"] == "success"


@pytest.mark.usefixtures("fake_service")
class TestAuthFailure:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "url", "payload"),
        [
            ("GET", "/de2api/auth/menuResource", None),
            ("GET", "/de2api/auth/busiResource/dataset", None),
            ("POST", "/de2api/auth/busiPermission", {"id": 1, "type": 1, "flag": "dataset"}),
            ("POST", "/de2api/auth/saveBusiPer", {"id": 1, "type": 1, "flag": "dataset", "permissions": []}),
        ],
    )
    async def test_missing_token_rejected(
        self,
        client: AsyncClient,
        method: str,
        url: str,
        payload: dict[str, Any] | None,
    ) -> None:
        if method == "GET":
            response = await client.get(url)
        else:
            response = await client.post(url, json=payload)

        assert response.status_code == 401
        _assert_result_message(response.json(), code=401)

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, client: AsyncClient) -> None:
        response = await client.get("/de2api/auth/menuResource", headers=INVALID_HEADERS)

        assert response.status_code == 401
        _assert_result_message(response.json(), code=401)


@pytest.mark.usefixtures("fake_service")
class TestSaveReadRoundTrip:
    @pytest.mark.asyncio
    async def test_save_busi_per_then_lookup_returns_saved_permissions(
        self,
        client: AsyncClient,
        fake_service: FakeAuthPermissionService,
    ) -> None:
        payload = {
            "id": 1,
            "type": 1,
            "flag": "dataset",
            "permissions": [{"id": 100, "weight": 7, "ext": 0}],
        }

        save_response = await client.post("/de2api/auth/saveBusiPer", headers=AUTH_HEADERS, json=payload)
        lookup_response = await client.post(
            "/de2api/auth/busiPermission",
            headers=AUTH_HEADERS,
            json={"id": 1, "type": 1, "flag": "dataset"},
        )

        _assert_result_message(save_response.json())
        body = lookup_response.json()
        _assert_result_message(body)
        assert len(fake_service.saved_busi_per[(1, 1, "dataset")]) == 1
        assert body["data"]["permissions"] == [{"id": 100, "weight": 7, "columnPermissions": None, "rowPermissions": None, "ext": 0}]

    @pytest.mark.asyncio
    async def test_save_menu_per_then_lookup_returns_saved_permissions(
        self,
        client: AsyncClient,
        fake_service: FakeAuthPermissionService,
    ) -> None:
        payload = {"id": 1, "permissions": [{"id": 5, "weight": 1, "ext": 0}]}

        save_response = await client.post("/de2api/auth/saveMenuPer", headers=AUTH_HEADERS, json=payload)
        lookup_response = await client.post("/de2api/auth/menuPermission", headers=AUTH_HEADERS, json={"id": 1})

        _assert_result_message(save_response.json())
        body = lookup_response.json()
        _assert_result_message(body)
        assert len(fake_service.saved_menu_per[1]) == 1
        assert body["data"]["permissions"] == [{"id": 5, "weight": 1, "columnPermissions": None, "rowPermissions": None, "ext": 0}]


class TestAuthorization:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("url", "payload"),
        [
            ("/de2api/auth/saveBusiPer", {"id": 1, "type": 1, "flag": "dataset", "permissions": []}),
            ("/de2api/auth/saveMenuPer", {"id": 1, "permissions": []}),
            (
                "/de2api/auth/saveBusiTargetPer",
                {"ids": [1], "type": 1, "flag": "dataset", "permissions": []},
            ),
            ("/de2api/auth/saveMenuTargetPer", {"ids": [1], "permissions": []}),
        ],
    )
    async def test_non_admin_cannot_save_permission_assignments(
        self,
        client: AsyncClient,
        url: str,
        payload: dict[str, Any],
    ) -> None:
        response = await client.post(url, headers=NON_ADMIN_HEADERS, json=payload)

        assert response.status_code == 403
        _assert_result_message(response.json(), code=403)


class TestServiceRepositoryBehavior:
    @pytest.mark.asyncio
    async def test_service_generates_permission_tree_from_repo_rows(self) -> None:
        service = AuthPermissionService(cast(Any, SimpleNamespace()))

        async def _get_menu_tree_nodes(_repo):
            return [
                SimpleNamespace(id=10, pid=0, menu_sort=1, name="root-menu", type=1, component=None),
                SimpleNamespace(id=11, pid=10, menu_sort=1, name="child-menu", type=2, component="view/index"),
            ]

        service.repo.get_menu_tree_nodes = MethodType(
            _get_menu_tree_nodes,
            service.repo,
        )

        tree = await service.get_menu_resource_tree(TokenUser(user_id=7, oid=9, language="zh-CN"))

        assert [node.name for node in tree] == ["root-menu"]
        assert tree[0].children[0].name == "child-menu"
        assert tree[0].children[0].leaf is True

    @pytest.mark.asyncio
    async def test_service_permission_lookup_maps_grants_to_permission_items(self) -> None:
        service = AuthPermissionService(cast(Any, SimpleNamespace()))

        async def _infer_target_type(_self, target_id: int, oid: int) -> str:
            del target_id, oid
            return "role"

        async def _get_menu_point_grants() -> dict[int, bool]:
            return {5: True, 8: False}

        service._infer_target_type = MethodType(_infer_target_type, service)
        service.repo.get_menu_point_grants = MethodType(
            lambda self, target_type, target_id, oid: _get_menu_point_grants(),
            service.repo,
        )

        result = await service.get_menu_permission(
            MenuPermissionRequest(id=99),
            TokenUser(user_id=7, oid=9, language="zh-CN"),
        )

        assert result.root is False
        assert result.readonly is True
        assert [(item.id, item.weight) for item in result.permissions] == [(5, 1), (8, 0)]

    @pytest.mark.asyncio
    async def test_repository_grant_lookup_returns_menu_grant_mapping(self) -> None:
        class _Result:
            def all(self):
                return [(5, True), (8, False)]

        class _Session:
            async def execute(self, statement):
                del statement
                return _Result()

        repo = AuthPermissionRepository(cast(Any, _Session()))

        assert await repo.get_menu_point_grants("role", 7, 9) == {5: True, 8: False}

    @pytest.mark.asyncio
    async def test_service_rejects_unsupported_busi_flag(self) -> None:
        service = AuthPermissionService(cast(Any, SimpleNamespace()))

        with pytest.raises(HTTPException) as exc_info:
            await service.get_busi_permission(
                BusiPermissionRequest(id=1, type=1, flag="invalid"),
                TokenUser(user_id=7, oid=9, language="zh-CN"),
            )

        assert exc_info.value.status_code == 400
