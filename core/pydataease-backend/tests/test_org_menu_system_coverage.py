# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from collections.abc import Sequence
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.org import CoreOrg  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.org import OrgCreateRequest, OrgEditRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.menu_service import MenuService, TITLE_MAP  # pyright: ignore[reportImplicitRelativeImport]
from app.services.org_service import OrgService, _build_tree  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sys_setting_service import SysSettingService  # pyright: ignore[reportImplicitRelativeImport]


class FakeOrgRepo:
    def __init__(self) -> None:
        self.all_orgs: list[Any] = []
        self.user_orgs: dict[int, list[Any]] = {}
        self.by_id: dict[int, Any] = {}
        self.children: dict[int, list[Any]] = {}
        self.created_payloads: list[dict[str, object]] = []
        self.updated_payloads: list[dict[str, object]] = []
        self.deleted: list[Any] = []

    async def list_all(self) -> list[Any]:
        return self.all_orgs

    async def get_user_orgs(self, user_id: int) -> list[Any]:
        return self.user_orgs.get(user_id, [])

    async def get_by_id(self, org_id: int) -> Any:
        return self.by_id.get(org_id)

    async def get_children(self, pid: int) -> list[Any]:
        return self.children.get(pid, [])

    async def create(self, payload: dict[str, object]) -> Any:
        self.created_payloads.append(payload)
        return SimpleNamespace(**payload)

    async def update(self, entity: Any, payload: dict[str, object]) -> Any:
        self.updated_payloads.append(payload)
        for key, value in payload.items():
            setattr(entity, key, value)
        return entity

    async def delete(self, entity: Any) -> None:
        self.deleted.append(entity)


class FakeMenuRepo:
    def __init__(self, rows: Sequence[Any]) -> None:
        self.rows = list(rows)

    async def list_all(self) -> list[Any]:
        return list(self.rows)


class FakeSysSettingRepo:
    def __init__(self) -> None:
        self.by_key: dict[str, Any] = {}
        self.by_type: dict[str, list[Any]] = {}
        self.raise_on_list = False
        self.raise_on_get = False

    async def list_by_type(self, setting_type: str) -> Sequence[Any]:
        if self.raise_on_list:
            raise AttributeError("boom")
        return self.by_type.get(setting_type, [])

    async def get_by_key(self, key: str) -> Any:
        if self.raise_on_get:
            raise TypeError("boom")
        return self.by_key.get(key)


def _org_service(repo: FakeOrgRepo) -> OrgService:
    return OrgService(session=cast(AsyncSession, cast(object, SimpleNamespace())), repository=cast(Any, repo))


def _token_user(user_id: int = 7, oid: int = 9) -> TokenUser:
    return TokenUser(user_id=user_id, oid=oid)


def _menu_row(menu_id: int, pid: int, name: str, *, type: int = 2, component: str | None = "Comp", auth: bool = False, path: str = "/demo", hidden: bool = False, in_layout: bool = True, icon: str | None = None) -> Any:
    return SimpleNamespace(id=menu_id, pid=pid, type=type, name=name, component=component, menu_sort=menu_id, icon=icon, path=path, hidden=hidden, in_layout=in_layout, auth=auth)


class TestOrgServiceCoverage:
    @pytest.mark.asyncio
    async def test_build_tree_marks_leaf_nodes_and_nests_children(self) -> None:
        tree = cast(list[dict[str, Any]], _build_tree([
            {"id": "1", "pid": "0", "name": "root-child"},
            {"id": "2", "pid": "1", "name": "leaf"},
        ]))

        assert tree[0]["leaf"] is False
        assert tree[0]["children"][0]["leaf"] is True

    @pytest.mark.asyncio
    async def test_tree_returns_full_tree_for_admin(self) -> None:
        repo = FakeOrgRepo()
        repo.all_orgs = [
            CoreOrg(id=10, pid=0, name="Sales", create_time=1, update_time=1),
            CoreOrg(id=11, pid=10, name="APAC", create_time=1, update_time=1),
        ]
        service = _org_service(repo)

        result = await service.tree(_token_user(user_id=1, oid=9))

        assert result[0].id == "0"
        assert result[0].children[0].name == "Sales"
        assert result[0].children[0].children[0].name == "APAC"

    @pytest.mark.asyncio
    async def test_tree_returns_empty_root_when_user_has_no_orgs(self) -> None:
        service = _org_service(FakeOrgRepo())

        result = await service.tree(_token_user())

        assert len(result) == 1
        assert result[0].id == "0"
        assert result[0].children == []

    @pytest.mark.asyncio
    async def test_tree_for_non_admin_includes_ancestors_and_descendants(self) -> None:
        repo = FakeOrgRepo()
        root = CoreOrg(id=10, pid=0, name="Sales", create_time=1, update_time=1)
        child = CoreOrg(id=11, pid=10, name="APAC", create_time=1, update_time=1)
        grandchild = CoreOrg(id=12, pid=11, name="Japan", create_time=1, update_time=1)
        unrelated = CoreOrg(id=13, pid=0, name="Other", create_time=1, update_time=1)
        repo.all_orgs = [root, child, grandchild, unrelated]
        repo.user_orgs[7] = [child]
        service = _org_service(repo)

        result = await service.tree(_token_user())

        assert result[0].children[0].name == "Sales"
        assert result[0].children[0].children[0].name == "APAC"
        assert result[0].children[0].children[0].children[0].name == "Japan"
        assert all(node.name != "Other" for node in result[0].children)

    @pytest.mark.asyncio
    async def test_create_requires_existing_parent_and_strips_name(self) -> None:
        repo = FakeOrgRepo()
        service = _org_service(repo)

        with pytest.raises(HTTPException) as exc:
            await service.create(OrgCreateRequest(name=" Child ", pid=999))

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_edit_delete_and_resource_exist_cover_core_paths(self) -> None:
        repo = FakeOrgRepo()
        repo.by_id[1] = CoreOrg(id=1, pid=0, name="Org", create_time=1, update_time=1)
        repo.by_id[2] = CoreOrg(id=2, pid=0, name="Parent", create_time=1, update_time=1)
        repo.children[2] = [CoreOrg(id=3, pid=2, name="Child", create_time=1, update_time=1)]
        service = _org_service(repo)

        created = await service.create(OrgCreateRequest(name=" New Org ", pid=0))
        edited = await service.edit(OrgEditRequest(id=1, name=" Edited "))
        exists = await service.resource_exist(2)
        with pytest.raises(HTTPException) as delete_exc:
            await service.delete(2)
        await service.delete(1)

        assert created.name == "New Org"
        assert edited.name == "Edited"
        assert exists is True
        assert delete_exc.value.status_code == 400
        assert repo.deleted[-1].id == 1

    @pytest.mark.asyncio
    async def test_collect_allowed_org_ids_and_missing_entity(self) -> None:
        user_org = CoreOrg(id=11, pid=10, name="APAC", create_time=1, update_time=1)
        all_orgs = [
            CoreOrg(id=10, pid=0, name="Sales", create_time=1, update_time=1),
            user_org,
            CoreOrg(id=12, pid=11, name="Japan", create_time=1, update_time=1),
        ]
        repo = FakeOrgRepo()
        service = _org_service(repo)

        assert service._collect_allowed_org_ids([user_org], all_orgs) == {10, 11, 12}
        with pytest.raises(HTTPException) as exc:
            await service._get_entity(999)
        assert exc.value.status_code == 404


class TestMenuServiceCoverage:
    @pytest.mark.asyncio
    async def test_build_children_skips_empty_directory_and_normalizes_path(self) -> None:
        service = MenuService.__new__(MenuService)
        service.session = cast(AsyncSession, cast(object, SimpleNamespace()))
        row_dir = _menu_row(1, 0, "data", type=1, component=None, path="/data")
        row_leaf = _menu_row(2, 0, "panel", path="/panel")
        row_child = _menu_row(3, 1, "dataset", path="/dataset")
        by_pid = {0: [row_dir, row_leaf], 1: [row_child]}

        result = service._build_children(0, by_pid)

        assert service._normalize_path("/dataset", 1) == "dataset"
        assert [item.name for item in result] == ["data", "panel"]
        assert result[0].meta.title == TITLE_MAP["data"]
        assert result[0].children[0].path == "dataset"

    @pytest.mark.asyncio
    async def test_get_menu_tree_returns_full_tree_for_admin_or_disabled_enforcement(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [_menu_row(1, 0, "panel", auth=True), _menu_row(2, 0, "workbranch", auth=False)]
        service = MenuService.__new__(MenuService)
        service.repo = FakeMenuRepo(rows)
        service.session = cast(AsyncSession, cast(object, SimpleNamespace()))
        monkeypatch.setattr("app.services.menu_service.get_settings", lambda: SimpleNamespace(permission_enforcement_enabled=False))

        disabled = await service.get_menu_tree(_token_user())
        monkeypatch.setattr("app.services.menu_service.get_settings", lambda: SimpleNamespace(permission_enforcement_enabled=True))
        admin = await service.get_menu_tree(_token_user(user_id=1))

        assert [item.name for item in disabled] == ["panel", "workbranch"]
        assert [item.name for item in admin] == ["panel", "workbranch"]

    @pytest.mark.asyncio
    async def test_get_menu_tree_filters_by_effective_ids_but_keeps_visible_parent_and_public_menu(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            _menu_row(10, 0, "sys-setting", type=1, component=None, auth=True, path="/sys-setting"),
            _menu_row(11, 10, "parameter", auth=True, path="/parameter"),
            _menu_row(12, 10, "dataset", auth=True, path="/dataset"),
            _menu_row(13, 0, "workbranch", auth=False, path="/workbranch"),
        ]
        service = MenuService.__new__(MenuService)
        service.repo = FakeMenuRepo(rows)
        service.session = cast(AsyncSession, cast(object, SimpleNamespace()))
        monkeypatch.setattr("app.services.menu_service.get_settings", lambda: SimpleNamespace(permission_enforcement_enabled=True))

        async def fake_effective_menu_ids(self: Any, user_id: int, oid: int) -> set[int]:
            assert (user_id, oid) == (7, 9)
            return {11}

        monkeypatch.setattr("app.services.menu_service.PermissionService.get_effective_menu_ids", fake_effective_menu_ids)
        result = await service.get_menu_tree(_token_user())

        assert [item.name for item in result] == ["sys-setting", "workbranch"]
        assert [child.name for child in result[0].children] == ["parameter"]

    @pytest.mark.asyncio
    async def test_build_children_filtered_hides_non_visible_leaf_nodes(self) -> None:
        service = MenuService.__new__(MenuService)
        row_visible = _menu_row(1, 0, "panel", auth=True)
        row_hidden = _menu_row(2, 0, "screen", auth=True)

        result = service._build_children_filtered(0, {0: [row_visible, row_hidden]}, {1})

        assert [item.name for item in result] == ["panel"]


class TestSysSettingServiceCoverage:
    @pytest.mark.asyncio
    async def test_get_ui_settings_returns_array_and_handles_repo_failure(self) -> None:
        repo = FakeSysSettingRepo()
        repo.by_type["ui"] = [SimpleNamespace(setting_key="theme", setting_value="dark"), SimpleNamespace(setting_key="lang", setting_value=None)]
        service = SysSettingService.__new__(SysSettingService)
        service.session = cast(AsyncSession, cast(object, SimpleNamespace()))
        service.repo = repo

        assert await service.get_ui_settings() == [{"key": "theme", "value": "dark"}, {"key": "lang", "value": ""}]
        repo.raise_on_list = True
        assert await service.get_ui_settings() == {}

    @pytest.mark.asyncio
    async def test_get_setting_and_default_settings_cover_fallbacks(self) -> None:
        repo = FakeSysSettingRepo()
        repo.by_key["defaultSettings.sort"] = SimpleNamespace(setting_value="desc")
        service = SysSettingService.__new__(SysSettingService)
        service.session = cast(AsyncSession, cast(object, SimpleNamespace()))
        service.repo = repo

        assert await service.get_setting("defaultSettings.sort") == "desc"
        assert await service.get_setting("missing") is None
        assert await service.get_default_settings() == {"sort": "desc"}
        repo.raise_on_get = True
        assert await service.get_default_settings() == {"sort": "asc"}

    @pytest.mark.asyncio
    async def test_get_i18n_share_base_and_default_login_cover_parsing_paths(self) -> None:
        repo = FakeSysSettingRepo()
        repo.by_key = {
            "i18nOptions": SimpleNamespace(setting_value='{"default":"zh-CN"}'),
            "shareBase.disable": SimpleNamespace(setting_value="false"),
            "shareBase.peRequire": SimpleNamespace(setting_value="true"),
            "defaultLogin": SimpleNamespace(setting_value="2"),
        }
        service = SysSettingService.__new__(SysSettingService)
        service.session = cast(AsyncSession, cast(object, SimpleNamespace()))
        service.repo = repo

        assert await service.get_i18n_options() == {"default": "zh-CN"}
        assert await service.get_share_base() == {"disable": False, "peRequire": True}
        assert await service.get_default_login() == 2
        repo.by_key["i18nOptions"] = SimpleNamespace(setting_value="not-json")
        repo.raise_on_get = False
        assert await service.get_i18n_options() == {}
