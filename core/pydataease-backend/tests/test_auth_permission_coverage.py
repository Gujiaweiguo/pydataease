# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from jose import jwt  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.login import LoginRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.auth_service import AuthService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import PermissionService  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.config import get_settings  # pyright: ignore[reportImplicitRelativeImport]
from app.utils.password_utils import derive_jwt_secret, hash_password  # pyright: ignore[reportImplicitRelativeImport]

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)"),
]
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


class FakeUserRepo:
    def __init__(self, account_user=None, id_user=None, updated_user=None) -> None:
        self.account_user = account_user
        self.id_user = id_user
        self.updated_user = updated_user
        self.updated_payloads: list[dict[str, object]] = []

    async def get_by_account(self, _account: str):
        return self.account_user

    async def get_by_id(self, _user_id: int):
        return self.id_user

    async def update(self, entity, payload: dict[str, object]):
        self.updated_payloads.append(payload)
        for key, value in payload.items():
            setattr(entity, key, value)
        return self.updated_user or entity


class FakeOrgRepo:
    def __init__(self, *, is_member: bool = False, user_orgs: list[Any] | None = None) -> None:
        self._is_member = is_member
        self._user_orgs = user_orgs or []

    async def is_member(self, _user_id: int, _oid: int) -> bool:
        return self._is_member

    async def get_user_orgs(self, _user_id: int) -> list[Any]:
        return self._user_orgs


def _auth_service(*, user_repo: FakeUserRepo, org_repo: FakeOrgRepo) -> AuthService:
    service = AuthService.__new__(AuthService)
    service.session = cast(AsyncSession, cast(object, SimpleNamespace()))
    object.__setattr__(service, "user_repo", user_repo)
    object.__setattr__(service, "org_repo", org_repo)
    object.__setattr__(service, "settings", get_settings())
    return service


def _permission_service(results: list[FakeScalarResult | FakeRowsResult]) -> PermissionService:
    return PermissionService(cast(AsyncSession, cast(object, FakeSession(results))))


class TestAuthServiceCoverage:
    async def test_login_returns_token_for_valid_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        password = "DataEase@123456"
        user = SimpleNamespace(id=101, password=hash_password(password), enable=True, oid=0)
        service = _auth_service(
            user_repo=FakeUserRepo(account_user=user),
            org_repo=FakeOrgRepo(user_orgs=[SimpleNamespace(id=9)]),
        )
        monkeypatch.setattr("app.services.auth_service.decrypt_rsa", lambda value: value)

        response = await service.login(LoginRequest(name="admin", pwd=password, origin=0))

        claims = jwt.decode(
            response.token,
            derive_jwt_secret(user.password),
            algorithms=[service.settings.jwt_algorithm],
        )
        assert claims["uid"] == 101
        assert claims["oid"] == 9
        assert response.exp > 0

    async def test_login_rejects_invalid_password(self, monkeypatch: pytest.MonkeyPatch) -> None:
        user = SimpleNamespace(id=101, password=hash_password("correct"), enable=True, oid=0)
        service = _auth_service(user_repo=FakeUserRepo(account_user=user), org_repo=FakeOrgRepo())
        monkeypatch.setattr("app.services.auth_service.decrypt_rsa", lambda value: value)

        with pytest.raises(HTTPException, match="用户名或密码错误"):
            await service.login(LoginRequest(name="admin", pwd="wrong", origin=0))

    async def test_refresh_with_org_rejects_disabled_user(self) -> None:
        user = SimpleNamespace(id=101, password=hash_password("pwd"), enable=False, oid=3)
        service = _auth_service(user_repo=FakeUserRepo(id_user=user), org_repo=FakeOrgRepo())

        with pytest.raises(HTTPException, match="用户不存在或已禁用"):
            await service.refresh_with_org(101, None)

    async def test_switch_org_rejects_non_member(self) -> None:
        user = SimpleNamespace(id=101, password=hash_password("pwd"), enable=True, oid=3)
        service = _auth_service(user_repo=FakeUserRepo(id_user=user), org_repo=FakeOrgRepo(is_member=False))

        with pytest.raises(HTTPException, match="User does not belong to the organization"):
            await service.switch_org(TokenUser(user_id=101, oid=3), 8)

    async def test_switch_org_updates_user_oid_and_issues_token(self) -> None:
        user = SimpleNamespace(id=101, password=hash_password("pwd"), enable=True, oid=3)
        repo = FakeUserRepo(id_user=user)
        service = _auth_service(user_repo=repo, org_repo=FakeOrgRepo(is_member=True))

        response = await service.switch_org(TokenUser(user_id=101, oid=3), 8)

        claims = jwt.decode(
            response.token,
            derive_jwt_secret(user.password),
            algorithms=[service.settings.jwt_algorithm],
        )
        assert repo.updated_payloads == [{"oid": 8}]
        assert claims["oid"] == 8

    async def test_switch_org_allows_admin_without_membership_check(self) -> None:
        user = SimpleNamespace(id=1, password=hash_password("pwd"), enable=True, oid=1)
        service = _auth_service(user_repo=FakeUserRepo(id_user=user), org_repo=FakeOrgRepo(is_member=False))

        response = await service.switch_org(TokenUser(user_id=1, oid=1), 88)

        claims = jwt.decode(
            response.token,
            derive_jwt_secret(user.password),
            algorithms=[service.settings.jwt_algorithm],
        )
        assert claims["uid"] == 1
        assert claims["oid"] == 88

    async def test_resolve_current_org_id_prefers_current_when_membership_exists(self) -> None:
        service = _auth_service(user_repo=FakeUserRepo(), org_repo=FakeOrgRepo(is_member=True))

        assert await service._resolve_current_org_id(7, 9) == 9

    async def test_resolve_current_org_id_falls_back_to_first_org_or_zero(self) -> None:
        with_orgs = _auth_service(
            user_repo=FakeUserRepo(),
            org_repo=FakeOrgRepo(is_member=False, user_orgs=[SimpleNamespace(id=12)]),
        )
        without_orgs = _auth_service(user_repo=FakeUserRepo(), org_repo=FakeOrgRepo(is_member=False, user_orgs=[]))

        assert await with_orgs._resolve_current_org_id(7, 9) == 12
        assert await without_orgs._resolve_current_org_id(7, 9) == 0

    async def test_get_dekey_delegates_to_helper(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _auth_service(user_repo=FakeUserRepo(), org_repo=FakeOrgRepo())
        monkeypatch.setattr("app.services.auth_service.get_dekey_response", lambda: "dekey-payload")

        assert await service.get_dekey() == "dekey-payload"

    async def test_issue_token_uses_password_derived_secret(self) -> None:
        password_hash = hash_password("Complex!123")
        service = _auth_service(user_repo=FakeUserRepo(), org_repo=FakeOrgRepo())

        response = service._issue_token(55, 77, password_hash)

        claims = jwt.decode(
            response.token,
            derive_jwt_secret(password_hash),
            algorithms=[service.settings.jwt_algorithm],
        )
        assert claims["uid"] == 55
        assert claims["oid"] == 77


class TestPermissionServiceCoverage:
    async def test_get_effective_menu_ids_combines_role_user_deny_and_org_permissions(self) -> None:
        service = _permission_service(
            [
                FakeRowsResult([(11,), (12,)]),
                FakeRowsResult([(100,), (101,), (101,)]),
                FakeRowsResult([(102,), (103,)]),
                FakeRowsResult([(101,), (999,)]),
                FakeRowsResult([(200,), (103,)]),
            ]
        )

        menu_ids = await service.get_effective_menu_ids(7, 9)

        assert menu_ids == {100, 102, 103, 200}

    async def test_get_effective_menu_ids_skips_role_query_when_user_has_no_roles(self) -> None:
        service = _permission_service(
            [
                FakeRowsResult([]),
                FakeRowsResult([(5,)]),
                FakeRowsResult([]),
                FakeRowsResult([(6,)]),
            ]
        )

        assert await service.get_effective_menu_ids(7, 9) == {5, 6}

    async def test_has_resource_permission_returns_true_when_enforcement_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        service = _permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: False))

        assert await service.has_resource_permission(TokenUser(user_id=7, oid=9), "dataset") is True

    async def test_has_resource_permission_returns_true_for_admin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(TokenUser(user_id=1, oid=9), "dataset") is True

    async def test_has_resource_permission_returns_true_when_point_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _permission_service([FakeScalarResult(None)])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(TokenUser(user_id=7, oid=9), "dataset") is True

    async def test_has_resource_permission_honors_role_grant(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _permission_service([FakeScalarResult(90), FakeRowsResult([(1,), (2,)]), FakeScalarResult(1)])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(TokenUser(user_id=7, oid=9), "dataset") is True

    async def test_has_resource_permission_honors_user_deny_after_no_grants(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _permission_service(
            [FakeScalarResult(90), FakeRowsResult([]), FakeScalarResult(None), FakeScalarResult(1)]
        )
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(TokenUser(user_id=7, oid=9), "dataset") is False

    async def test_has_resource_permission_uses_org_grant_as_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _permission_service(
            [FakeScalarResult(90), FakeRowsResult([]), FakeScalarResult(None), FakeScalarResult(None), FakeScalarResult(1)]
        )
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        assert await service.has_resource_permission(TokenUser(user_id=7, oid=9), "dataset") is True

    async def test_require_resource_access_raises_403_when_denied(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        async def deny(_user: TokenUser, _resource_type: str, _permission_type: str = "use") -> bool:
            return False

        monkeypatch.setattr(service, "has_resource_permission", deny)

        with pytest.raises(HTTPException, match="Access denied"):
            await service.require_resource_access(TokenUser(user_id=7, oid=9), "dataset")

    async def test_require_resource_access_short_circuits_for_admin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = _permission_service([])
        monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

        await service.require_resource_access(TokenUser(user_id=1, oid=9), "dataset", "manage")
