# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.role import (  # pyright: ignore[reportImplicitRelativeImport]
    RoleCreateRequest,
    RoleEditRequest,
    RoleMountRequest,
    RoleQueryRequest,
    RoleUnmountRequest,
    RoleUserOptionRequest,
)
from app.schemas.user import (  # pyright: ignore[reportImplicitRelativeImport]
    UserByCurrentOrgRequest,
    UserCreateRequest,
    UserEditRequest,
    UserEnableRequest,
    UserPagerRequest,
    UserRoleSelectedRequest,
)
from app.services.role_service import RoleService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.user_service import DEFAULT_PASSWORD, SYSTEM_ADMIN_ROLE_ID, UserService  # pyright: ignore[reportImplicitRelativeImport]
from app.utils.password_utils import verify_password  # pyright: ignore[reportImplicitRelativeImport]

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)"),
]
class FakeScalarResult:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one(self) -> Any:
        return self._value


class FakeRowsResult:
    def __init__(self, rows: list[tuple[Any, ...]] | list[Any]) -> None:
        self._rows = rows

    def all(self) -> list[Any]:
        return list(self._rows)

    def scalars(self) -> "FakeRowsResult":
        return self


class FakeSession:
    def __init__(self, results: list[FakeScalarResult | FakeRowsResult] | None = None) -> None:
        self._results = results or []
        self.executed: list[Any] = []
        self.added: list[Any] = []
        self.commit_count = 0

    async def execute(self, statement=None, _params=None):
        self.executed.append(statement)
        if not self._results:
            raise AssertionError("No fake results remaining for execute()")
        return self._results.pop(0)

    async def commit(self) -> None:
        self.commit_count += 1

    def add(self, entity: Any) -> None:
        self.added.append(entity)


class FakeUserRepo:
    def __init__(self) -> None:
        self.by_id: dict[int, Any] = {}
        self.by_account: dict[str, Any] = {}
        self.created_payloads: list[dict[str, object]] = []
        self.updated_payloads: list[dict[str, object]] = []
        self.deleted: list[Any] = []
        self.search_result: tuple[list[Any], int] = ([], 0)
        self.list_all_result: list[Any] = []

    async def get_by_id(self, user_id: int):
        return self.by_id.get(user_id)

    async def get_by_account(self, account: str):
        return self.by_account.get(account)

    async def create(self, payload: dict[str, object]):
        self.created_payloads.append(payload)
        entity = SimpleNamespace(**payload)
        self.by_id[entity.id] = entity
        self.by_account[entity.account] = entity
        return entity

    async def update(self, entity, payload: dict[str, object]):
        self.updated_payloads.append(payload)
        for key, value in payload.items():
            setattr(entity, key, value)
        return entity

    async def delete(self, entity) -> None:
        self.deleted.append(entity)

    async def search(self, **_kwargs):
        return self.search_result

    async def list_all(self):
        return self.list_all_result


class FakeRoleRepo:
    def __init__(self) -> None:
        self.by_id: dict[int, Any] = {}
        self.created_payloads: list[dict[str, object]] = []
        self.updated_payloads: list[dict[str, object]] = []
        self.deleted: list[Any] = []
        self.user_roles_result: list[Any] = []
        self.role_users_result: list[Any] = []
        self.in_role: dict[tuple[int, int, int], bool] = {}
        self.bound: list[tuple[int, int, int]] = []
        self.unbound: list[tuple[int, int, int]] = []
        self.list_by_org_result: list[Any] = []

    async def get_by_id(self, role_id: int):
        return self.by_id.get(role_id)

    async def create(self, payload: dict[str, object]):
        self.created_payloads.append(payload)
        entity = SimpleNamespace(**payload)
        self.by_id[entity.id] = entity
        return entity

    async def update(self, entity, payload: dict[str, object]):
        self.updated_payloads.append(payload)
        for key, value in payload.items():
            setattr(entity, key, value)
        return entity

    async def delete(self, entity) -> None:
        self.deleted.append(entity)

    async def get_user_roles(self, _user_id: int, _oid: int):
        return self.user_roles_result

    async def get_role_users(self, _role_id: int):
        return self.role_users_result

    async def is_user_in_role(self, user_id: int, role_id: int, oid: int) -> bool:
        return self.in_role.get((user_id, role_id, oid), False)

    async def bind_user(self, role_id: int, user_id: int, oid: int):
        self.bound.append((role_id, user_id, oid))

    async def unbind_user(self, role_id: int, user_id: int, oid: int):
        self.unbound.append((role_id, user_id, oid))

    async def list_by_org(self, _oid: int):
        return self.list_by_org_result


class FakeOrgRepo:
    def __init__(self) -> None:
        self.memberships: dict[tuple[int, int], bool] = {}
        self.orgs_by_user: dict[int, list[Any]] = {}
        self.users_by_org: dict[int, list[Any]] = {}
        self.orgs_by_id: dict[int, Any] = {}

    async def is_member(self, user_id: int, oid: int) -> bool:
        return self.memberships.get((user_id, oid), False)

    async def get_user_orgs(self, user_id: int):
        return self.orgs_by_user.get(user_id, [])

    async def get_org_users(self, oid: int):
        return self.users_by_org.get(oid, [])

    async def get_by_id(self, oid: int):
        return self.orgs_by_id.get(oid)


def _user_service(
    *,
    session: FakeSession | None = None,
    user_repo: FakeUserRepo | None = None,
    role_repo: FakeRoleRepo | None = None,
    org_repo: FakeOrgRepo | None = None,
) -> UserService:
    service = UserService.__new__(UserService)
    service.session = cast(AsyncSession, cast(object, session or FakeSession()))
    object.__setattr__(service, "user_repo", user_repo or FakeUserRepo())
    object.__setattr__(service, "role_repo", role_repo or FakeRoleRepo())
    object.__setattr__(service, "org_repo", org_repo or FakeOrgRepo())
    return service


def _role_service(
    *,
    session: FakeSession | None = None,
    role_repo: FakeRoleRepo | None = None,
    org_repo: FakeOrgRepo | None = None,
    user_repo: FakeUserRepo | None = None,
) -> RoleService:
    service = RoleService.__new__(RoleService)
    service.session = cast(AsyncSession, cast(object, session or FakeSession()))
    object.__setattr__(service, "role_repo", role_repo or FakeRoleRepo())
    object.__setattr__(service, "org_repo", org_repo or FakeOrgRepo())
    object.__setattr__(service, "user_repo", user_repo or FakeUserRepo())
    return service


def _token_user(*, user_id: int = 7, oid: int = 9) -> TokenUser:
    return TokenUser(user_id=user_id, oid=oid)


class TestUserServiceCoverage:
    async def test_pager_normalizes_page_and_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        repo = FakeUserRepo()
        repo.search_result = ([SimpleNamespace(id=1)], 1)
        service = _user_service(user_repo=repo)

        async def fake_build_user_items(users: list[Any]) -> list[Any]:
            return [
                {
                    "id": item.id,
                    "account": f"acct-{item.id}",
                    "name": f"name-{item.id}",
                    "enable": True,
                }
                for item in users
            ]

        monkeypatch.setattr(service, "_build_user_items", fake_build_user_items)

        response = await service.pager(0, 0, UserPagerRequest(keyword="abc", enable=True), _token_user())

        assert response.total == 1
        assert response.items[0].id == 1

    async def test_create_rejects_duplicate_account(self) -> None:
        repo = FakeUserRepo()
        repo.by_account["dup"] = SimpleNamespace(id=1)
        service = _user_service(user_repo=repo)

        with pytest.raises(HTTPException, match="Account already exists"):
            await service.create(UserCreateRequest(account="dup", name="name", oid=9), _token_user())

    async def test_create_rejects_cross_org_creation_for_non_admin(self) -> None:
        service = _user_service()

        with pytest.raises(HTTPException, match="Cannot create user outside current organization"):
            await service.create(UserCreateRequest(account="u1", name="name", oid=99), _token_user())

    async def test_create_success_hashes_default_password_and_binds_roles(self, monkeypatch: pytest.MonkeyPatch) -> None:
        repo = FakeUserRepo()
        org_repo = FakeOrgRepo()
        org_repo.memberships[(7, 9)] = True
        service = _user_service(user_repo=repo, org_repo=org_repo)
        called: dict[str, Any] = {"membership": None, "bindings": None}

        async def fake_validate(_role_ids, _oid):
            return None

        async def fake_membership(user_id: int, oid: int):
            called["membership"] = (user_id, oid)

        async def fake_bindings(user_id: int, oid: int, role_ids: list[int]):
            called["bindings"] = (user_id, oid, role_ids)

        async def fake_query(user_id: int, _user: TokenUser):
            return SimpleNamespace(id=user_id, role_ids=[5, 6])

        monkeypatch.setattr(service, "_validate_role_ids", fake_validate)
        monkeypatch.setattr(service, "_ensure_user_org_membership", fake_membership)
        monkeypatch.setattr(service, "_replace_role_bindings", fake_bindings)
        monkeypatch.setattr(service, "query_by_id", fake_query)

        response = await service.create(
            UserCreateRequest(account="  acct  ", name="  User  ", email=" a@b.com ", phone=" 123 ", role_ids=[5, 6], oid=9),
            _token_user(),
        )

        created = repo.created_payloads[0]
        assert created["account"] == "acct"
        assert created["name"] == "User"
        assert created["email"] == "a@b.com"
        assert created["phone"] == "123"
        assert verify_password(DEFAULT_PASSWORD, cast(str, created["password"])) is True
        assert called["membership"] == (response.id, 9)
        assert called["bindings"] == (response.id, 9, [5, 6])

    async def test_edit_updates_fields_and_role_bindings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entity = SimpleNamespace(id=15, name="old", email="old@a.com", phone="0")
        repo = FakeUserRepo()
        service = _user_service(user_repo=repo)
        async def fake_manageable_user(_uid: int, _user: TokenUser):
            return entity

        monkeypatch.setattr(service, "_get_manageable_user", fake_manageable_user)

        async def fake_validate(_role_ids, _oid):
            return None

        bindings: list[tuple[int, int, list[int]]] = []

        async def fake_bindings(user_id: int, oid: int, role_ids: list[int]):
            bindings.append((user_id, oid, role_ids))

        async def fake_query(user_id: int, _user: TokenUser):
            return SimpleNamespace(id=user_id, name=entity.name, email=entity.email, phone=entity.phone)

        monkeypatch.setattr(service, "_validate_role_ids", fake_validate)
        monkeypatch.setattr(service, "_replace_role_bindings", fake_bindings)
        monkeypatch.setattr(service, "query_by_id", fake_query)

        response = await service.edit(
            UserEditRequest(id=15, name="  new  ", email=" x@y.com ", phone=" 188 ", role_ids=[3, 4]),
            _token_user(),
        )

        assert repo.updated_payloads[0]["name"] == "new"
        assert repo.updated_payloads[0]["email"] == "x@y.com"
        assert repo.updated_payloads[0]["phone"] == "188"
        assert bindings == [(15, 9, [3, 4])]
        assert response.name == "new"

    async def test_delete_blocks_system_admin(self) -> None:
        service = _user_service()

        with pytest.raises(HTTPException, match="System administrator cannot be deleted"):
            await service.delete(1, _token_user(user_id=1, oid=0))

    async def test_delete_removes_bindings_and_user(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entity = SimpleNamespace(id=19)
        repo = FakeUserRepo()
        session = FakeSession(results=[FakeRowsResult([]), FakeRowsResult([])])
        service = _user_service(session=session, user_repo=repo)
        async def fake_manageable_user(_uid: int, _user: TokenUser):
            return entity

        async def fake_ensure(_uid: int):
            return None

        monkeypatch.setattr(service, "_get_manageable_user", fake_manageable_user)
        monkeypatch.setattr(service, "_ensure_not_last_admin", fake_ensure)

        await service.delete(19, _token_user())

        assert session.commit_count == 1
        assert repo.deleted == [entity]

    async def test_enable_false_checks_last_admin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entity = SimpleNamespace(id=20, enable=True)
        repo = FakeUserRepo()
        service = _user_service(user_repo=repo)
        calls: list[int] = []
        async def fake_manageable_user(_uid: int, _user: TokenUser):
            return entity

        monkeypatch.setattr(service, "_get_manageable_user", fake_manageable_user)

        async def fake_ensure(uid: int):
            calls.append(uid)

        monkeypatch.setattr(service, "_ensure_not_last_admin", fake_ensure)

        await service.enable(UserEnableRequest(id=20, enable=False), _token_user())

        assert calls == [20]
        assert repo.updated_payloads[0]["enable"] is False

    async def test_reset_password_sets_default_hash(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entity = SimpleNamespace(id=21, password="old")
        repo = FakeUserRepo()
        service = _user_service(user_repo=repo)
        async def fake_manageable_user(_uid: int, _user: TokenUser):
            return entity

        monkeypatch.setattr(service, "_get_manageable_user", fake_manageable_user)

        await service.reset_password(21, _token_user())

        assert verify_password(DEFAULT_PASSWORD, cast(str, repo.updated_payloads[0]["password"])) is True

    async def test_query_by_id_builds_detail_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entity = SimpleNamespace(
            id=25,
            account="acct",
            name="User",
            email="u@example.com",
            phone="123",
            enable=True,
            oid=9,
            create_time=1,
            update_time=2,
        )
        org_repo = FakeOrgRepo()
        org_repo.orgs_by_user[25] = [SimpleNamespace(id=9, name="Org", pid=0)]
        service = _user_service(org_repo=org_repo)
        async def fake_manageable_user(_uid: int, _user: TokenUser):
            return entity

        async def fake_get_user_roles(_user_id: int, _oid: int, _is_admin: bool):
            return [SimpleNamespace(id=3, name="role", description=None, oid=9, type=1)]

        monkeypatch.setattr(service, "_get_manageable_user", fake_manageable_user)
        monkeypatch.setattr(service, "_get_user_roles", fake_get_user_roles)

        response = await service.query_by_id(25, _token_user())

        assert response.id == 25
        assert response.role_ids == [3]
        assert response.org_ids == [9]

    async def test_default_password_and_by_current_org_filtering(self) -> None:
        org_repo = FakeOrgRepo()
        org_repo.users_by_org[9] = [
            SimpleNamespace(id=1, account="alpha", name="Alice", email="a@x.com", phone="1", enable=True, oid=9, create_time=1, update_time=1),
            SimpleNamespace(id=2, account="beta", name="Bob", email="b@x.com", phone="2", enable=True, oid=9, create_time=1, update_time=1),
        ]
        service = _user_service(session=FakeSession(), org_repo=org_repo)

        async def fake_build_user_items(users: list[Any]) -> list[Any]:
            return [SimpleNamespace(account=item.account) for item in users]

        service._build_user_items = fake_build_user_items  # type: ignore[method-assign]

        default_password = await service.default_password()
        filtered = await service.by_current_org(UserByCurrentOrgRequest(keyword="ali"), _token_user())

        assert default_password.password == DEFAULT_PASSWORD
        assert [item.account for item in filtered] == ["alpha"]

    async def test_users_in_role_builds_paged_result(self, monkeypatch: pytest.MonkeyPatch) -> None:
        session = FakeSession(results=[FakeRowsResult([SimpleNamespace(id=31)]), FakeScalarResult(1)])
        service = _user_service(session=session)

        async def fake_role_in_scope(_rid: int, _user: TokenUser):
            return SimpleNamespace(id=3)

        async def fake_build_user_items(users: list[Any]) -> list[Any]:
            return [
                {
                    "id": item.id,
                    "account": f"acct-{item.id}",
                    "name": f"name-{item.id}",
                    "enable": True,
                }
                for item in users
            ]

        monkeypatch.setattr(service, "_get_role_in_scope", fake_role_in_scope)
        monkeypatch.setattr(service, "_build_user_items", fake_build_user_items)

        response = await service.users_in_role(1, 10, UserRoleSelectedRequest(role_id=3), _token_user())

        assert response.total == 1
        assert response.items[0].id == 31

    async def test_manageable_user_and_role_validation_helpers(self) -> None:
        repo = FakeUserRepo()
        org_repo = FakeOrgRepo()
        service = _user_service(user_repo=repo, org_repo=org_repo)

        with pytest.raises(HTTPException, match="User not found"):
            await service._get_manageable_user(999, _token_user())

        repo.by_id[8] = SimpleNamespace(id=8)
        with pytest.raises(HTTPException, match="User not found"):
            await service._get_manageable_user(8, _token_user())

    async def test_validate_role_ids_and_membership_helpers(self) -> None:
        session = FakeSession(results=[FakeRowsResult([(1,), (2,)]), FakeScalarResult(1)])
        role_repo = FakeRoleRepo()
        role_repo.in_role[(7, SYSTEM_ADMIN_ROLE_ID, 0)] = True
        org_repo = FakeOrgRepo()
        org_repo.orgs_by_id[9] = SimpleNamespace(id=9, name="Org")
        service = _user_service(session=session, role_repo=role_repo, org_repo=org_repo)

        await service._validate_role_ids([1, 2, 2], 9)

        with pytest.raises(HTTPException, match="Cannot disable or delete the last administrator"):
            await service._ensure_not_last_admin(7)

    async def test_ensure_user_org_membership_and_static_helpers(self) -> None:
        session = FakeSession()
        org_repo = FakeOrgRepo()
        org_repo.orgs_by_id[9] = SimpleNamespace(id=9)
        service = _user_service(session=session, org_repo=org_repo)

        await service._ensure_user_org_membership(7, 0)
        await service._ensure_user_org_membership(7, 9)

        assert len(session.added) == 1
        assert session.commit_count == 1
        assert UserService._resolve_target_oid(9, _token_user()) == 9
        candidate = cast(Any, SimpleNamespace(account="acct", name="Name", email="e@x.com", phone="188"))
        assert UserService._matches_keyword(candidate, "name") is True


class TestRoleServiceCoverage:
    async def test_query_filters_roles_by_keyword(self) -> None:
        role_repo = FakeRoleRepo()
        role_repo.list_by_org_result = [
            SimpleNamespace(id=1, name="Admin", description=None, oid=9, type=0, create_time=1, update_time=1),
            SimpleNamespace(id=2, name="Analyst", description=None, oid=9, type=1, create_time=1, update_time=1),
        ]
        service = _role_service(role_repo=role_repo)

        response = await service.query(RoleQueryRequest(keyword="anal"), _token_user())

        assert [item.id for item in response] == [2]

    async def test_create_requires_current_org_and_success_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        role_repo = FakeRoleRepo()
        service = _role_service(role_repo=role_repo)

        with pytest.raises(HTTPException, match="Current organization is required"):
            await service.create(RoleCreateRequest(name="Role"), _token_user(oid=0))

        async def fake_available(_name: str, _oid: int, _exclude_id: int | None):
            return None

        monkeypatch.setattr(service, "_ensure_role_name_available", fake_available)
        response = await service.create(RoleCreateRequest(name="  Role  ", description=" desc "), _token_user())

        assert role_repo.created_payloads[0]["name"] == "Role"
        assert response.name == "Role"

    async def test_edit_and_detail_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        role = SimpleNamespace(id=6, name="Old", description="d", oid=9, type=1, create_time=1, update_time=1)
        role_repo = FakeRoleRepo()
        role_repo.role_users_result = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
        service = _role_service(role_repo=role_repo)
        async def fake_manageable_role(_rid: int, _user: TokenUser):
            return role

        async def fake_visible_role(_rid: int, _user: TokenUser):
            return role

        monkeypatch.setattr(service, "_get_manageable_role", fake_manageable_role)
        monkeypatch.setattr(service, "_get_visible_role", fake_visible_role)

        async def fake_available(_name: str, _oid: int, _exclude_id: int | None):
            return None

        monkeypatch.setattr(service, "_ensure_role_name_available", fake_available)
        updated = await service.edit(RoleEditRequest(id=6, name="  New  ", description=" desc "), _token_user())
        detail = await service.detail(6, _token_user())

        assert updated.name == "New"
        assert detail.member_count == 2

    async def test_delete_and_by_org(self, monkeypatch: pytest.MonkeyPatch) -> None:
        role = SimpleNamespace(id=7, name="Role", description=None, oid=9, type=1, create_time=1, update_time=1)
        role_repo = FakeRoleRepo()
        role_repo.list_by_org_result = [role]
        session = FakeSession(results=[FakeRowsResult([])])
        service = _role_service(session=session, role_repo=role_repo)
        async def fake_manageable_role(_rid: int, _user: TokenUser):
            return role

        monkeypatch.setattr(service, "_get_manageable_role", fake_manageable_role)

        await service.delete(7, _token_user())
        listed = await service.by_org(None, _token_user())

        assert role_repo.deleted == [role]
        assert [item.id for item in listed] == [7]

    async def test_user_option_and_external_user_search(self) -> None:
        session = FakeSession(
            results=[
                FakeRowsResult([SimpleNamespace(id=1, account="alpha", name="Alice", email=None, phone=None, enable=True)]),
                FakeRowsResult([SimpleNamespace(id=2, account="beta", name="Bob", email=None, phone=None, enable=True)]),
            ]
        )
        service = _role_service(session=session)

        options = await service.user_option(RoleUserOptionRequest(keyword="ali"), _token_user())
        external = await service.search_external_user(" bob ", _token_user())
        empty = await service.search_external_user("   ", _token_user())

        assert [item.id for item in options] == [1]
        assert [item.id for item in external] == [2]
        assert empty == []

    async def test_mount_and_unmount_user_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        role = SimpleNamespace(id=9, oid=9, type=1)
        role_repo = FakeRoleRepo()
        role_repo.in_role[(100, 9, 9)] = False
        role_repo.in_role[(101, 9, 9)] = True
        user_repo = FakeUserRepo()
        user_repo.by_id[100] = SimpleNamespace(id=100)
        session = FakeSession(results=[FakeScalarResult(0)])
        service = _role_service(session=session, role_repo=role_repo, user_repo=user_repo)
        async def fake_visible_role(_rid: int, _user: TokenUser):
            return role

        async def fake_bindable_user(user_id: int, _user: TokenUser):
            return SimpleNamespace(id=user_id)

        monkeypatch.setattr(service, "_get_visible_role", fake_visible_role)
        monkeypatch.setattr(service, "_get_bindable_user", fake_bindable_user)

        await service.mount_user(RoleMountRequest(role_id=9, user_ids=[100, 100, 101]), _token_user())

        assert role_repo.bound == [(9, 100, 9)]

        role_repo.in_role[(100, 9, 9)] = False
        async def fake_count_user_roles(_user_id: int) -> int:
            return 0

        monkeypatch.setattr(service, "_count_user_roles", fake_count_user_roles)
        await service.unmount_user(RoleUnmountRequest(role_id=9, user_ids=[100]), _token_user())

        assert role_repo.unbound == [(9, 100, 9)]
        assert len(user_repo.deleted) == 1
        assert user_repo.deleted[0].id == 100

    async def test_role_helpers_cover_visibility_name_and_binding_errors(self) -> None:
        role_repo = FakeRoleRepo()
        user_repo = FakeUserRepo()
        org_repo = FakeOrgRepo()
        service = _role_service(
            session=FakeSession(results=[FakeScalarResult(1)]),
            role_repo=role_repo,
            user_repo=user_repo,
            org_repo=org_repo,
        )

        with pytest.raises(HTTPException, match="Role not found"):
            await service._get_visible_role(1, _token_user())

        role_repo.by_id[2] = SimpleNamespace(id=2, oid=9, type=0)
        with pytest.raises(HTTPException, match="Built-in roles cannot be modified"):
            await service._get_manageable_role(2, _token_user())

        with pytest.raises(HTTPException, match="Role name already exists"):
            await service._ensure_role_name_available("dup", 9, None)

        with pytest.raises(HTTPException, match="User not found"):
            await service._get_bindable_user(8, _token_user())

        user_repo.by_id[8] = SimpleNamespace(id=8)
        with pytest.raises(HTTPException, match="User is not in current organization"):
            await service._get_bindable_user(8, _token_user())

        with pytest.raises(HTTPException, match="Current organization is required"):
            RoleService._require_current_org(_token_user(oid=0))
