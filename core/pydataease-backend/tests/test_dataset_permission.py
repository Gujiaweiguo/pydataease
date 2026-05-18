from __future__ import annotations

from collections.abc import Generator
from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import get_dataset_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import (  # pyright: ignore[reportImplicitRelativeImport]
    PermissionService,
    get_permission_service,
)
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.dataset_fixtures import (  # pyright: ignore[reportImplicitRelativeImport]
    FakeDatasetService,
)


class FakeScalarResult:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        return self._value


class FakeRowsResult:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows

    def all(self) -> list[tuple[Any, ...]]:
        return self._rows


class FakeSession:
    def __init__(self, results: list[FakeScalarResult | FakeRowsResult]) -> None:
        self._results = results

    async def execute(self, _statement=None, _params=None):
        if not self._results:
            raise AssertionError("No fake results remaining for execute()")
        return self._results.pop(0)


def build_permission_service(results: list[FakeScalarResult | FakeRowsResult]) -> PermissionService:
    return PermissionService(cast(AsyncSession, cast(object, FakeSession(results))))


class DenyAllPermissionService:
    async def require_resource_access(self, _user, _resource_type, _permission_type="use"):
        raise HTTPException(status_code=403, detail="Access denied")

    async def has_resource_permission(self, _user, _resource_type, _permission_type="use"):
        return False

    async def get_effective_menu_ids(self, _user_id, _oid):
        return set()


@pytest.fixture
def token_user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def deny_all_dataset_service() -> Generator[FakeDatasetService, None, None]:
    service = FakeDatasetService()
    app.dependency_overrides[get_dataset_service] = lambda: service
    app.dependency_overrides[get_permission_service] = lambda: DenyAllPermissionService()
    yield service
    _ = app.dependency_overrides.pop(get_dataset_service, None)
    _ = app.dependency_overrides.pop(get_permission_service, None)


class TestPermissionServiceBehavior:
    @pytest.mark.asyncio
    async def test_require_resource_access_raises_403_when_enforced_and_denied(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        async def deny(_user: TokenUser, _resource_type: str, _permission_type: str = "use") -> bool:
            return False

        monkeypatch.setattr(service, "has_resource_permission", deny)

        with pytest.raises(HTTPException, match="Access denied"):
            await service.require_resource_access(token_user, "dataset", "use")

    @pytest.mark.asyncio
    async def test_require_resource_access_passes_when_enforcement_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: False))

        await service.require_resource_access(token_user, "dataset", "use")

    @pytest.mark.asyncio
    async def test_require_resource_access_passes_for_admin_user(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = build_permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        await service.require_resource_access(TokenUser(user_id=1, oid=9), "dataset", "manage")

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_true_when_enforcement_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: False))

        assert await service.has_resource_permission(token_user, "dataset", "use") is True

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_true_for_admin_user(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = build_permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(TokenUser(user_id=1, oid=9), "dataset", "use") is True

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_true_when_permission_point_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service([FakeScalarResult(None)])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(token_user, "dataset", "use") is True

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_true_for_role_grant(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service(
            [
                FakeScalarResult(99),
                FakeRowsResult([(101,), (202,)]),
                FakeScalarResult(1),
            ]
        )
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(token_user, "dataset", "use") is True

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_true_for_user_grant(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service(
            [
                FakeScalarResult(99),
                FakeRowsResult([]),
                FakeScalarResult(1),
            ]
        )
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(token_user, "dataset", "use") is True

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_false_for_user_deny(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service(
            [
                FakeScalarResult(99),
                FakeRowsResult([]),
                FakeScalarResult(None),
                FakeScalarResult(1),
            ]
        )
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(token_user, "dataset", "use") is False

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_true_for_org_grant(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service(
            [
                FakeScalarResult(99),
                FakeRowsResult([]),
                FakeScalarResult(None),
                FakeScalarResult(None),
                FakeScalarResult(1),
            ]
        )
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(token_user, "dataset", "use") is True

    @pytest.mark.asyncio
    async def test_has_resource_permission_returns_false_without_grants(
        self,
        monkeypatch: pytest.MonkeyPatch,
        token_user: TokenUser,
    ) -> None:
        service = build_permission_service(
            [
                FakeScalarResult(99),
                FakeRowsResult([]),
                FakeScalarResult(None),
                FakeScalarResult(None),
                FakeScalarResult(None),
            ]
        )
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(token_user, "dataset", "use") is False


class TestDatasetPermissionEndpoints:
    @pytest.mark.asyncio
    async def test_dataset_tree_returns_403_when_permission_denied(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        deny_all_dataset_service: FakeDatasetService,
    ) -> None:
        assert deny_all_dataset_service.created == []
        response = await client.post("/de2api/datasetTree/tree", headers=auth_headers, json={"busiFlag": "dataset"})

        assert response.status_code == 403
        assert response.json()["msg"] == "Access denied"

    @pytest.mark.asyncio
    async def test_dataset_create_returns_403_when_permission_denied(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        deny_all_dataset_service: FakeDatasetService,
    ) -> None:
        response = await client.post(
            "/de2api/datasetTree/create",
            headers=auth_headers,
            json={"name": "blocked", "pid": 0, "nodeType": "folder"},
        )

        assert response.status_code == 403
        assert response.json()["msg"] == "Access denied"
        assert deny_all_dataset_service.created == []

    @pytest.mark.asyncio
    async def test_dataset_save_returns_403_when_permission_denied(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        deny_all_dataset_service: FakeDatasetService,
    ) -> None:
        response = await client.post(
            "/de2api/datasetTree/save",
            headers=auth_headers,
            json={"id": 10, "name": "blocked", "nodeType": "dataset"},
        )

        assert response.status_code == 403
        assert response.json()["msg"] == "Access denied"
        assert deny_all_dataset_service.saved == []

    @pytest.mark.asyncio
    async def test_dataset_rename_now_requires_permission(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        deny_all_dataset_service: FakeDatasetService,
    ) -> None:
        response = await client.post(
            "/de2api/datasetTree/rename",
            headers=auth_headers,
            json={"id": 300, "name": "renamed"},
        )

        assert response.status_code == 403
        assert response.json()["msg"] == "Access denied"
        assert deny_all_dataset_service.renamed == []

    @pytest.mark.asyncio
    async def test_dataset_move_now_requires_permission(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        deny_all_dataset_service: FakeDatasetService,
    ) -> None:
        response = await client.post(
            "/de2api/datasetTree/move",
            headers=auth_headers,
            json={"id": 400, "pid": 5},
        )

        assert response.status_code == 403
        assert response.json()["msg"] == "Access denied"
        assert deny_all_dataset_service.moved == []

    @pytest.mark.asyncio
    async def test_dataset_delete_now_requires_permission(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        deny_all_dataset_service: FakeDatasetService,
    ) -> None:
        response = await client.post("/de2api/datasetTree/delete/999", headers=auth_headers)

        assert response.status_code == 403
        assert response.json()["msg"] == "Access denied"
        assert deny_all_dataset_service.deleted_ids == []

    @pytest.mark.asyncio
    async def test_dataset_per_delete_now_requires_permission(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        deny_all_dataset_service: FakeDatasetService,
    ) -> None:
        response = await client.post("/de2api/datasetTree/perDelete/999", headers=auth_headers)

        assert response.status_code == 403
        assert response.json()["msg"] == "Access denied"
        assert deny_all_dataset_service.deleted_ids == []
