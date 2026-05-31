from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dataset_repo import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetFieldRepository,
    DatasetGroupRepository,
    DatasetTableRepository,
)

from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import DatasetGroupCreate, DatasetGroupUpdate  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import DatasetService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import PermissionService  # pyright: ignore[reportImplicitRelativeImport]


class FakeGroupRepo:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []
        self.updated: list[dict[str, object]] = []
        self.group = SimpleNamespace(
            id=222,
            name="existing-dataset",
            pid=0,
            level=0,
            node_type="dataset",
            type="db",
            mode=0,
            info={"datasourceId": 2001, "table": "orders"},
            create_by="7",
            create_time=0,
            update_by="7",
            last_update_time=0,
            is_cross=False,
        )

    async def list_all_ordered(self):
        return [self.group]

    async def create(self, payload: dict[str, object]):
        self.created.append(payload)
        return SimpleNamespace(**payload)

    async def get_by_id(self, group_id: int):
        if group_id == self.group.id:
            return self.group
        return None

    async def update(self, existing, payload: dict[str, object]):
        self.updated.append(payload)
        data = existing.__dict__ | payload
        self.group = SimpleNamespace(**data)
        return self.group


class FakeTableRepo:
    async def list_by_group(self, _dataset_group_id: int):
        return []


class FakeFieldRepo:
    async def delete_by_group(self, _dataset_group_id: int) -> None:
        return None

    async def list_by_group(self, _dataset_group_id: int):
        return []


def _result_name(result: object) -> object:
    if isinstance(result, dict):
        return result.get("name")
    return getattr(result, "name", None)


@pytest.fixture
def dataset_service(monkeypatch: pytest.MonkeyPatch) -> DatasetService:
    service = DatasetService(
        session=cast(AsyncSession, cast(object, SimpleNamespace())),
        group_repo=cast(DatasetGroupRepository, cast(object, FakeGroupRepo())),
        table_repo=cast(DatasetTableRepository, cast(object, FakeTableRepo())),
        field_repo=cast(DatasetFieldRepository, cast(object, FakeFieldRepo())),
    )

    async def fake_sync_dataset_source(_group_id: int, _group_name: str, _info: object):
        return None

    monkeypatch.setattr(service, "_sync_dataset_source", fake_sync_dataset_source)
    return service


@pytest.mark.asyncio
async def test_view_only_datasource_permission_blocks_dataset_create(
    dataset_service: DatasetService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

    async def deny(_self: PermissionService, _user: TokenUser, _resource_type: str, _permission_type: str = "use") -> bool:
        return False

    monkeypatch.setattr(PermissionService, "has_resource_permission", deny)

    with pytest.raises(HTTPException, match="Access denied") as exc:
        await dataset_service.create(
            DatasetGroupCreate(
                name="orders-dataset",
                node_type="dataset",
                type="db",
                mode=0,
                datasource_id=2001,
                table_name="orders",
            ),
            TokenUser(user_id=7, oid=9),
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_view_only_datasource_permission_blocks_dataset_edit(
    dataset_service: DatasetService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

    async def deny(_self: PermissionService, _user: TokenUser, _resource_type: str, _permission_type: str = "use") -> bool:
        return False

    monkeypatch.setattr(PermissionService, "has_resource_permission", deny)

    with pytest.raises(HTTPException, match="Access denied") as exc:
        await dataset_service.save(
            DatasetGroupUpdate(
                id=222,
                name="orders-dataset-updated",
                datasource_id=2001,
                table_name="orders",
            ),
            TokenUser(user_id=7, oid=9),
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_manage_permission_allows_dataset_create_and_edit(
    dataset_service: DatasetService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

    async def allow(_self: PermissionService, _user: TokenUser, _resource_type: str, _permission_type: str = "use") -> bool:
        return True

    monkeypatch.setattr(PermissionService, "has_resource_permission", allow)

    created = await dataset_service.create(
        DatasetGroupCreate(
            name="orders-dataset",
            node_type="dataset",
            type="db",
            mode=0,
            datasource_id=2001,
            table_name="orders",
        ),
        TokenUser(user_id=7, oid=9),
    )
    updated = await dataset_service.save(
        DatasetGroupUpdate(
            id=222,
            name="orders-dataset-updated",
            datasource_id=2001,
            table_name="orders",
        ),
        TokenUser(user_id=7, oid=9),
    )

    assert _result_name(created) == "orders-dataset"
    assert _result_name(updated) == "orders-dataset-updated"


@pytest.mark.asyncio
async def test_admin_bypasses_datasource_manage_check(
    dataset_service: DatasetService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: True))

    async def should_not_run(_self: PermissionService, _user: TokenUser, _resource_type: str, _permission_type: str = "use") -> bool:
        raise AssertionError("admin should bypass permission lookup")

    monkeypatch.setattr(PermissionService, "has_resource_permission", should_not_run)

    created = await dataset_service.create(
        DatasetGroupCreate(
            name="admin-dataset",
            node_type="dataset",
            type="db",
            mode=0,
            datasource_id=2001,
            table_name="orders",
        ),
        TokenUser(user_id=1, oid=1),
    )
    updated = await dataset_service.save(
        DatasetGroupUpdate(
            id=222,
            name="admin-dataset-updated",
            datasource_id=2001,
            table_name="orders",
        ),
        TokenUser(user_id=1, oid=1),
    )

    assert _result_name(created) == "admin-dataset"
    assert _result_name(updated) == "admin-dataset-updated"
