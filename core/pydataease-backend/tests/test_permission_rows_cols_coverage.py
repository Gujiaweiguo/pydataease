# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.column_permission import CoreColumnPermission  # pyright: ignore[reportImplicitRelativeImport]
from app.models.permission_whitelist import CorePermissionWhitelist  # pyright: ignore[reportImplicitRelativeImport]
from app.models.row_permission import CoreRowPermission  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.column_permission import (  # pyright: ignore[reportImplicitRelativeImport]
    ColumnPermissionCreateRequest,
    ColumnPermissionListRequest,
    ColumnPermissionUpdateRequest,
)
from app.schemas.row_permission import (  # pyright: ignore[reportImplicitRelativeImport]
    RowPermissionCreateRequest,
    RowPermissionListRequest,
    RowPermissionUpdateRequest,
)
from app.services.column_permission_service import ColumnPermissionService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.row_permission_service import RowPermissionService, _validate_filter_sql  # pyright: ignore[reportImplicitRelativeImport]


class FakeScalarResult:
    def __init__(self, values: list[Any]) -> None:
        self._values = values

    def all(self) -> list[Any]:
        return list(self._values)

    def scalar_one_or_none(self) -> Any:
        return self._values[0] if self._values else None


class FakeExecuteResult:
    def __init__(self, values: list[Any]) -> None:
        self._values = values

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self._values)

    def scalar_one_or_none(self) -> Any:
        return self._values[0] if self._values else None


class FakeSession:
    def __init__(self, execute_results: list[Any] | None = None) -> None:
        self.execute_results = execute_results or []
        self.added: list[Any] = []
        self.deleted: list[Any] = []
        self.commit_count = 0
        self.refresh_count = 0

    async def execute(self, _statement: Any) -> Any:
        if not self.execute_results:
            raise AssertionError("No fake execute result remaining")
        result = self.execute_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def add(self, entity: Any) -> None:
        self.added.append(entity)

    async def delete(self, entity: Any) -> None:
        self.deleted.append(entity)

    async def commit(self) -> None:
        self.commit_count += 1

    async def refresh(self, _entity: Any) -> None:
        self.refresh_count += 1


def _user(user_id: int = 7, oid: int = 9) -> TokenUser:
    return TokenUser(user_id=user_id, oid=oid)


class TestColumnPermissionServiceCoverage:
    @pytest.mark.asyncio
    async def test_list_rules_returns_serialized_rules_for_admin(self) -> None:
        rule = CoreColumnPermission(id=1, dataset_id=8, field_id=9, target_type="user", target_id=7, action="mask", enabled=True, create_time=1, update_time=1)
        service = ColumnPermissionService(cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([rule])]))))

        result = await service.list_rules(ColumnPermissionListRequest(dataset_id=8), _user(user_id=1))

        assert result[0].action == "mask"
        assert result[0].dataset_id == 8

    @pytest.mark.asyncio
    async def test_create_rule_rejects_invalid_action(self) -> None:
        service = ColumnPermissionService(cast(AsyncSession, cast(object, FakeSession())))

        with pytest.raises(HTTPException) as exc:
            await service.create_rule(
                ColumnPermissionCreateRequest(dataset_id=8, field_id=9, target_type="user", target_id=7, action="bad", enabled=True),
                _user(user_id=1),
            )

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_rule_persists_and_refreshes_entity(self) -> None:
        session = FakeSession()
        service = ColumnPermissionService(cast(AsyncSession, cast(object, session)))

        result = await service.create_rule(
            ColumnPermissionCreateRequest(dataset_id=8, field_id=9, target_type="user", target_id=7, action="mask", enabled=False),
            _user(user_id=1),
        )

        assert len(session.added) == 1
        assert session.added[0].enabled is False
        assert result.action == "mask"
        assert session.commit_count == 1
        assert session.refresh_count == 1

    @pytest.mark.asyncio
    async def test_update_rule_raises_when_rule_missing_or_action_invalid(self) -> None:
        missing = ColumnPermissionService(cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([])]))))
        invalid = ColumnPermissionService(
            cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([
                CoreColumnPermission(id=1, dataset_id=8, field_id=9, target_type="user", target_id=7, action="mask", enabled=True, create_time=1, update_time=1)
            ])])))
        )

        with pytest.raises(HTTPException) as missing_exc:
            await missing.update_rule(ColumnPermissionUpdateRequest(id=99, action="mask"), _user(user_id=1))
        with pytest.raises(HTTPException) as invalid_exc:
            await invalid.update_rule(ColumnPermissionUpdateRequest(id=1, action="bad"), _user(user_id=1))

        assert missing_exc.value.status_code == 404
        assert invalid_exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_rule_updates_fields(self) -> None:
        rule = CoreColumnPermission(id=1, dataset_id=8, field_id=9, target_type="user", target_id=7, action="mask", enabled=True, create_time=1, update_time=1)
        session = FakeSession([FakeExecuteResult([rule])])
        service = ColumnPermissionService(cast(AsyncSession, cast(object, session)))

        updated = await service.update_rule(ColumnPermissionUpdateRequest(id=1, action="disable", enabled=False), _user(user_id=1))

        assert updated.action == "disable"
        assert updated.enabled is False
        assert session.commit_count == 1
        assert session.refresh_count == 1

    @pytest.mark.asyncio
    async def test_delete_rule_requires_manage_permission_for_non_admin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rule = CoreColumnPermission(id=1, dataset_id=8, field_id=9, target_type="user", target_id=7, action="mask", enabled=True, create_time=1, update_time=1)
        service = ColumnPermissionService(cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([rule])]))))

        async def fake_has_permission(self: Any, user: TokenUser, resource_type: str, permission_type: str) -> bool:
            assert (user.user_id, resource_type, permission_type) == (7, "dataset", "manage")
            return False

        monkeypatch.setattr("app.services.column_permission_service.PermissionService.has_resource_permission", fake_has_permission)
        with pytest.raises(HTTPException) as exc:
            await service.delete_rule(1, _user())
        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_rule_deletes_entity_for_admin(self) -> None:
        rule = CoreColumnPermission(id=1, dataset_id=8, field_id=9, target_type="user", target_id=7, action="mask", enabled=True, create_time=1, update_time=1)
        session = FakeSession([FakeExecuteResult([rule])])
        service = ColumnPermissionService(cast(AsyncSession, cast(object, session)))

        await service.delete_rule(1, _user(user_id=1))

        assert session.deleted == [rule]
        assert session.commit_count == 1


class TestRowPermissionServiceCoverage:
    @pytest.mark.asyncio
    async def test_validate_filter_sql_blocks_dangerous_keywords(self) -> None:
        _validate_filter_sql("region = 'east'")
        with pytest.raises(HTTPException) as exc:
            _validate_filter_sql("delete from sales")
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_list_rules_and_create_rule_cover_admin_path(self) -> None:
        existing = CoreRowPermission(id=1, dataset_id=8, target_type="user", target_id=7, filter_sql="region='east'", enabled=True, create_time=1, update_time=1)
        session = FakeSession([FakeExecuteResult([existing])])
        service = RowPermissionService(cast(AsyncSession, cast(object, session)))

        listed = await service.list_rules(RowPermissionListRequest(dataset_id=8), _user(user_id=1))
        created = await service.create_rule(
            RowPermissionCreateRequest(dataset_id=8, target_type="role", target_id=2, filter_sql="region='west'", enabled=False),
            _user(user_id=1),
        )

        assert listed[0].filter_sql == "region='east'"
        assert created.enabled is False
        assert len(session.added) == 1
        assert session.commit_count == 1
        assert session.refresh_count == 1

    @pytest.mark.asyncio
    async def test_update_rule_rejects_missing_and_invalid_sql(self) -> None:
        missing = RowPermissionService(cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([])]))))
        rule = CoreRowPermission(id=1, dataset_id=8, target_type="user", target_id=7, filter_sql="a=1", enabled=True, create_time=1, update_time=1)
        invalid = RowPermissionService(cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([rule])]))))

        with pytest.raises(HTTPException) as missing_exc:
            await missing.update_rule(RowPermissionUpdateRequest(id=99, filter_sql="a=1"), _user(user_id=1))
        with pytest.raises(HTTPException) as invalid_exc:
            await invalid.update_rule(RowPermissionUpdateRequest(id=1, filter_sql="drop table x"), _user(user_id=1))

        assert missing_exc.value.status_code == 404
        assert invalid_exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_rule_and_delete_rule_cover_success_paths(self) -> None:
        rule = CoreRowPermission(id=1, dataset_id=8, target_type="user", target_id=7, filter_sql="a=1", enabled=True, create_time=1, update_time=1)
        delete_rule = CoreRowPermission(id=2, dataset_id=8, target_type="user", target_id=7, filter_sql="b=1", enabled=True, create_time=1, update_time=1)
        session = FakeSession([FakeExecuteResult([rule]), FakeExecuteResult([delete_rule])])
        service = RowPermissionService(cast(AsyncSession, cast(object, session)))

        updated = await service.update_rule(RowPermissionUpdateRequest(id=1, filter_sql="a=2", enabled=False), _user(user_id=1))
        await service.delete_rule(2, _user(user_id=1))

        assert updated.filter_sql == "a=2"
        assert updated.enabled is False
        assert session.deleted == [delete_rule]
        assert session.commit_count == 2

    @pytest.mark.asyncio
    async def test_list_whitelist_is_admin_only_and_serializes_entries(self) -> None:
        entry = CorePermissionWhitelist(id=1, user_id=7, dataset_id=8, scope="row", create_time=123)
        service = RowPermissionService(cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([entry])]))))

        with pytest.raises(HTTPException) as exc:
            await service.list_whitelist(_user())
        result = await service.list_whitelist(_user(user_id=1))

        assert exc.value.status_code == 403
        assert result == [{"id": 1, "user_id": 7, "dataset_id": 8, "scope": "row", "create_time": 123}]

    @pytest.mark.asyncio
    async def test_add_whitelist_and_remove_whitelist_cover_all_paths(self) -> None:
        created_entry = CorePermissionWhitelist(id=1, user_id=7, dataset_id=8, scope="both", create_time=123)
        session = FakeSession([FakeExecuteResult([created_entry])])
        service = RowPermissionService(cast(AsyncSession, cast(object, session)))

        with pytest.raises(HTTPException) as create_exc:
            await service.add_whitelist(7, 8, "both", _user())
        created = await service.add_whitelist(7, 8, "both", _user(user_id=1))
        with pytest.raises(HTTPException) as missing_exc:
            await RowPermissionService(cast(AsyncSession, cast(object, FakeSession([FakeExecuteResult([])])))).remove_whitelist(99, _user(user_id=1))
        await service.remove_whitelist(1, _user(user_id=1))

        assert create_exc.value.status_code == 403
        assert created["scope"] == "both"
        assert missing_exc.value.status_code == 404
        assert len(session.added) == 1
        assert len(session.deleted) == 1

    @pytest.mark.asyncio
    async def test_require_manage_uses_permission_service_for_non_admin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = RowPermissionService(cast(AsyncSession, cast(object, FakeSession())))

        async def fake_has_permission(self: Any, user: TokenUser, resource_type: str, permission_type: str) -> bool:
            return resource_type == "dataset" and permission_type == "manage" and user.user_id == 7

        monkeypatch.setattr("app.services.row_permission_service.PermissionService.has_resource_permission", fake_has_permission)
        await service._require_manage(_user(), 8)
