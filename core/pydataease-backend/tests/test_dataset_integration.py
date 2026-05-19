from __future__ import annotations

import os
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.repositories.dataset_repo import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetFieldRepository,
    DatasetGroupRepository,
    DatasetTableRepository,
)
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetGroupCreate,
    DatasetGroupMove,
    DatasetGroupRename,
)
from app.services.dataset_service import DatasetService  # pyright: ignore[reportImplicitRelativeImport]

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.getenv("DE_E2E") != "1",
        reason="Requires PostgreSQL (set DE_E2E=1)",
    ),
]


def _group_payload(
    stamp: int,
    *,
    name_prefix: str = "test-folder",
    pid: int | None = None,
    level: int = 0,
    node_type: str = "folder",
    info: object = None,
) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"{name_prefix}-{stamp}",
        "pid": pid,
        "level": level,
        "node_type": node_type,
        "type": None,
        "mode": None,
        "info": info,
        "create_by": "7",
        "create_time": now,
        "update_by": "7",
        "last_update_time": now,
        "is_cross": None,
    }


def _table_payload(stamp: int, *, group_id: int, name_prefix: str = "test-table") -> dict[str, object]:
    return {
        "id": _stamp(),
        "name": f"{name_prefix}-{stamp}",
        "table_name": f"test_table_{stamp}",
        "datasource_id": None,
        "dataset_group_id": group_id,
        "type": "db",
        "info": None,
    }


def _field_payload(
    stamp: int,
    *,
    group_id: int,
    table_id: int | None,
    origin_name: str = "col_a",
    name: str = "Column A",
    dataease_name: str | None = None,
    field_short_name: str | None = None,
    group_type: str = "d",
    checked: bool = True,
    chart_id: int | None = None,
    ext_field: int = 0,
    column_index: int = 0,
) -> dict[str, object]:
    _ = stamp
    resolved_name = dataease_name or origin_name
    resolved_short_name = field_short_name or origin_name
    return {
        "id": _stamp(),
        "datasource_id": None,
        "dataset_table_id": table_id,
        "dataset_group_id": group_id,
        "chart_id": chart_id,
        "origin_name": origin_name,
        "name": name,
        "dataease_name": resolved_name,
        "field_short_name": resolved_short_name,
        "group_type": group_type,
        "type": "VARCHAR",
        "size": 255,
        "de_type": 0,
        "de_extract_type": 0,
        "ext_field": ext_field,
        "checked": checked,
        "column_index": column_index,
    }


async def _create_group(
    repo: DatasetGroupRepository,
    stamp: int,
    *,
    name_prefix: str = "test-folder",
    pid: int | None = None,
    level: int = 0,
    node_type: str = "folder",
    info: object = None,
):
    return await repo.create(
        _group_payload(
            stamp,
            name_prefix=name_prefix,
            pid=pid,
            level=level,
            node_type=node_type,
            info=info,
        )
    )


def _service(session: AsyncSession) -> DatasetService:
    return DatasetService(
        session=session,
        group_repo=DatasetGroupRepository(session),
        table_repo=DatasetTableRepository(session),
        field_repo=DatasetFieldRepository(session),
    )


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


class TestDatasetGroupRepositoryIntegration:
    async def test_create_and_get_by_id_round_trip(self, db_session: AsyncSession) -> None:
        repo = DatasetGroupRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            created = await _create_group(repo, stamp, name_prefix="repo-create")
            created_ids.append(created.id)

            fetched = await repo.get_by_id(created.id)

            assert fetched is not None
            assert fetched.id == created.id
            assert fetched.name == f"repo-create-{stamp}"
            assert fetched.node_type == "folder"
        finally:
            for gid in reversed(created_ids):
                await repo.delete_cascade(gid)

    async def test_list_all_ordered_returns_created_groups(self, db_session: AsyncSession) -> None:
        repo = DatasetGroupRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            first = await _create_group(repo, stamp, name_prefix="repo-list-a")
            second = await _create_group(repo, stamp, name_prefix="repo-list-b")
            created_ids.extend([first.id, second.id])

            groups = await repo.list_all_ordered()
            group_ids = {group.id for group in groups}

            assert first.id in group_ids
            assert second.id in group_ids
        finally:
            for gid in reversed(created_ids):
                await repo.delete_cascade(gid)

    async def test_get_children_returns_direct_children(self, db_session: AsyncSession) -> None:
        repo = DatasetGroupRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            parent = await _create_group(repo, stamp, name_prefix="repo-parent")
            child_one = await _create_group(
                repo, stamp, name_prefix="repo-child-a", pid=parent.id, level=1
            )
            child_two = await _create_group(
                repo, stamp, name_prefix="repo-child-b", pid=parent.id, level=1
            )
            created_ids.append(parent.id)

            children = await repo.get_children(parent.id)
            child_ids = {child.id for child in children}

            assert child_one.id in child_ids
            assert child_two.id in child_ids
            assert all(child.pid == parent.id for child in children)
        finally:
            for gid in reversed(created_ids):
                await repo.delete_cascade(gid)

    async def test_get_children_excludes_non_children(self, db_session: AsyncSession) -> None:
        repo = DatasetGroupRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            parent = await _create_group(repo, stamp, name_prefix="repo-parent-filter")
            sibling_root = await _create_group(repo, stamp, name_prefix="repo-sibling-root")
            child = await _create_group(
                repo, stamp, name_prefix="repo-child-filter", pid=parent.id, level=1
            )
            created_ids.extend([parent.id, sibling_root.id])

            children = await repo.get_children(parent.id)
            child_ids = {node.id for node in children}

            assert child.id in child_ids
            assert sibling_root.id not in child_ids
        finally:
            for gid in reversed(created_ids):
                await repo.delete_cascade(gid)

    async def test_delete_cascade_deletes_group_children_tables_and_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        root = await _create_group(group_repo, stamp, name_prefix="repo-delete-root")
        try:
            child_folder = await _create_group(
                group_repo, stamp, name_prefix="repo-delete-child", pid=root.id, level=1
            )
            dataset = await _create_group(
                group_repo,
                stamp,
                name_prefix="repo-delete-dataset",
                pid=child_folder.id,
                level=2,
                node_type="dataset",
            )
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="repo-delete-table"))
            field = await field_repo.create(
                _field_payload(stamp, group_id=dataset.id, table_id=table.id, origin_name="root_col")
            )

            await group_repo.delete_cascade(root.id)

            assert await group_repo.get_by_id(root.id) is None
            assert await group_repo.get_by_id(child_folder.id) is None
            assert await group_repo.get_by_id(dataset.id) is None
            assert await table_repo.get_by_id(table.id) is None
            assert await field_repo.get_by_id(field.id) is None
        finally:
            if await group_repo.get_by_id(root.id) is not None:
                await group_repo.delete_cascade(root.id)


class TestDatasetTableRepositoryIntegration:
    async def test_create_and_list_by_group_round_trip(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="table-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="table-rt"))

            tables = await table_repo.list_by_group(group.id)

            assert [item.id for item in tables] == [table.id]
            assert tables[0].dataset_group_id == group.id
            assert tables[0].table_name == f"test_table_{stamp}"
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_by_group_returns_multiple_tables(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="table-multi-group")
            created_ids.append(group.id)
            first = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="table-multi-a"))
            second = await table_repo.create(
                _table_payload(stamp + 1, group_id=group.id, name_prefix="table-multi-b")
            )

            tables = await table_repo.list_by_group(group.id)
            table_ids = {table.id for table in tables}

            assert first.id in table_ids
            assert second.id in table_ids
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_by_group_excludes_other_group_tables(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group_a = await _create_group(group_repo, stamp, name_prefix="table-filter-a")
            group_b = await _create_group(group_repo, stamp, name_prefix="table-filter-b")
            created_ids.extend([group_a.id, group_b.id])
            owned = await table_repo.create(_table_payload(stamp, group_id=group_a.id, name_prefix="table-owned"))
            other = await table_repo.create(_table_payload(stamp + 1, group_id=group_b.id, name_prefix="table-other"))

            tables = await table_repo.list_by_group(group_a.id)

            assert {table.id for table in tables} == {owned.id}
            assert other.id not in {table.id for table in tables}
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)


class TestDatasetFieldRepositoryIntegration:
    async def test_create_and_list_by_group_round_trip(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="field-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="field-table"))
            field = await field_repo.create(_field_payload(stamp, group_id=group.id, table_id=table.id))

            fields = await field_repo.list_by_group(group.id)

            assert [item.id for item in fields] == [field.id]
            assert fields[0].origin_name == "col_a"
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_by_table_round_trip(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="field-table-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="field-table-rt"))
            first = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_a", column_index=0)
            )
            second = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_b", name="Column B", column_index=1)
            )

            fields = await field_repo.list_by_table(table.id)

            assert [field.id for field in fields] == [first.id, second.id]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_by_group_orders_by_column_index(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="field-order-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="field-order-table"))
            late = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_z", column_index=2)
            )
            early = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_a", column_index=0)
            )

            fields = await field_repo.list_by_group(group.id)

            assert [field.id for field in fields] == [early.id, late.id]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_save_field_updates_existing_field(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="field-save-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="field-save-table"))
            field = await field_repo.create(_field_payload(stamp, group_id=group.id, table_id=table.id))

            updated = await field_repo.save_field(
                {
                    "id": field.id,
                    "dataset_group_id": group.id,
                    "dataset_table_id": table.id,
                    "origin_name": "col_a",
                    "name": "Column A Updated",
                    "dataease_name": "col_a_updated",
                    "field_short_name": "col_a_updated",
                    "group_type": "q",
                    "type": "VARCHAR",
                    "de_type": 0,
                    "de_extract_type": 0,
                    "ext_field": 0,
                    "checked": False,
                    "column_index": 3,
                }
            )
            fetched = await field_repo.get_by_id(field.id)

            assert updated.id == field.id
            assert fetched is not None
            assert fetched.name == "Column A Updated"
            assert fetched.group_type == "q"
            assert fetched.checked is False
            assert fetched.column_index == 3
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_delete_by_group_removes_all_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="field-delete-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="field-delete-table"))
            await field_repo.create(_field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_a"))
            await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_b", column_index=1)
            )

            await field_repo.delete_by_group(group.id)

            assert await field_repo.list_by_group(group.id) == []
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_checked_by_group_filters_checked_without_chart(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="field-checked-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="field-checked-table"))
            eligible = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_ok", checked=True, chart_id=None)
            )
            await field_repo.create(
                _field_payload(
                    stamp,
                    group_id=group.id,
                    table_id=table.id,
                    origin_name="col_unchecked",
                    checked=False,
                    column_index=1,
                )
            )
            await field_repo.create(
                _field_payload(
                    stamp,
                    group_id=group.id,
                    table_id=table.id,
                    origin_name="col_chart",
                    checked=True,
                    chart_id=_stamp(),
                    column_index=2,
                )
            )

            fields = await field_repo.list_checked_by_group(group.id)

            assert [field.id for field in fields] == [eligible.id]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_checked_by_group_keeps_column_index_order(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="field-checked-order-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="field-checked-order-table"))
            second = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_b", column_index=1)
            )
            first = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_a", column_index=0)
            )

            fields = await field_repo.list_checked_by_group(group.id)

            assert [field.id for field in fields] == [first.id, second.id]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_origin_fields_by_groups_returns_multi_group_mapping(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group_a = await _create_group(group_repo, stamp, name_prefix="origin-group-a")
            group_b = await _create_group(group_repo, stamp, name_prefix="origin-group-b")
            created_ids.extend([group_a.id, group_b.id])
            table_a = await table_repo.create(_table_payload(stamp, group_id=group_a.id, name_prefix="origin-table-a"))
            table_b = await table_repo.create(_table_payload(stamp + 1, group_id=group_b.id, name_prefix="origin-table-b"))
            field_a = await field_repo.create(
                _field_payload(stamp, group_id=group_a.id, table_id=table_a.id, origin_name="col_a")
            )
            field_b = await field_repo.create(
                _field_payload(stamp, group_id=group_b.id, table_id=table_b.id, origin_name="col_b")
            )

            mapping = await field_repo.list_origin_fields_by_groups([group_a.id, group_b.id])

            assert [field.id for field in mapping[str(group_a.id)]] == [field_a.id]
            assert [field.id for field in mapping[str(group_b.id)]] == [field_b.id]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_list_origin_fields_by_groups_excludes_chart_and_ext_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="origin-filter-group")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="origin-filter-table"))
            eligible = await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_ok")
            )
            await field_repo.create(
                _field_payload(
                    stamp,
                    group_id=group.id,
                    table_id=table.id,
                    origin_name="col_chart",
                    chart_id=_stamp(),
                    column_index=1,
                )
            )
            await field_repo.create(
                _field_payload(
                    stamp,
                    group_id=group.id,
                    table_id=table.id,
                    origin_name="col_ext",
                    ext_field=1,
                    column_index=2,
                )
            )

            mapping = await field_repo.list_origin_fields_by_groups([group.id])

            assert [field.id for field in mapping[str(group.id)]] == [eligible.id]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)


class TestDatasetServiceIntegration:
    async def test_tree_builds_correct_hierarchy_from_db(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            folder = await _create_group(group_repo, stamp, name_prefix="svc-tree-root")
            child_folder = await _create_group(
                group_repo, stamp, name_prefix="svc-tree-child", pid=folder.id, level=1
            )
            dataset = await _create_group(
                group_repo,
                stamp,
                name_prefix="svc-tree-dataset",
                pid=child_folder.id,
                level=2,
                node_type="dataset",
            )
            created_ids.append(folder.id)

            tree = cast(list[dict[str, Any]], await svc.tree())
            root_children = cast(list[dict[str, Any]], tree[0]["children"])
            folder_node = next(node for node in root_children if node["id"] == str(folder.id))
            child_node = cast(list[dict[str, Any]], folder_node["children"])[0]
            dataset_node = cast(list[dict[str, Any]], child_node["children"])[0]

            assert tree[0]["id"] == "0"
            assert folder_node["name"] == folder.name
            assert folder_node["leaf"] is False
            assert child_node["id"] == str(child_folder.id)
            assert dataset_node["id"] == str(dataset.id)
            assert dataset_node["leaf"] is True
            assert dataset_node["pid"] == str(child_folder.id)
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_create_creates_group_and_returns_correct_response(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            response = await svc.create(
                DatasetGroupCreate(name=f"svc-create-{stamp}", pid=0, node_type="folder"),
                _user(),
            )
            created_ids.append(response.id)
            stored = await group_repo.get_by_id(response.id)

            assert stored is not None
            assert response.id == stored.id
            assert response.name == f"svc-create-{stamp}"
            assert response.pid is None
            assert response.level == 0
            assert response.node_type == "folder"
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_create_under_parent_sets_pid_and_level(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            parent = await _create_group(group_repo, stamp, name_prefix="svc-parent")
            created_ids.append(parent.id)
            response = await svc.create(
                DatasetGroupCreate(name=f"svc-child-{stamp}", pid=parent.id, node_type="folder"),
                _user(),
            )
            child = await group_repo.get_by_id(response.id)

            assert child is not None
            assert child.pid == parent.id
            assert child.level == 1
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_create_persists_all_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            response = await svc.create(
                DatasetGroupCreate(
                    name=f"svc-create-fields-{stamp}",
                    pid=0,
                    node_type="dataset",
                    all_fields=[
                        {
                            "originName": "col_a",
                            "name": "Column A",
                            "dataeaseName": "col_a",
                            "fieldShortName": "col_a",
                            "groupType": "d",
                            "type": "VARCHAR",
                            "deType": 0,
                            "deExtractType": 0,
                            "extField": 0,
                            "checked": True,
                            "columnIndex": 0,
                        },
                        {
                            "originName": "col_b",
                            "name": "Column B",
                            "dataeaseName": "col_b",
                            "fieldShortName": "col_b",
                            "groupType": "q",
                            "type": "VARCHAR",
                            "deType": 0,
                            "deExtractType": 0,
                            "extField": 0,
                            "checked": False,
                            "columnIndex": 1,
                        },
                    ],
                ),
                _user(),
            )
            created_ids.append(response.id)

            fields = await field_repo.list_by_group(response.id)

            assert len(fields) == 2
            assert [field.origin_name for field in fields] == ["col_a", "col_b"]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_rename_updates_name_in_db(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="svc-rename")
            created_ids.append(group.id)

            response = await svc.rename(
                DatasetGroupRename(id=group.id, name=f"svc-renamed-{stamp}"),
                _user(),
            )
            stored = await group_repo.get_by_id(group.id)

            assert response.name == f"svc-renamed-{stamp}"
            assert stored is not None
            assert stored.name == f"svc-renamed-{stamp}"
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_move_changes_pid_and_level_in_db(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            parent = await _create_group(group_repo, stamp, name_prefix="svc-move-parent")
            destination = await _create_group(group_repo, stamp, name_prefix="svc-move-dest")
            child = await _create_group(group_repo, stamp, name_prefix="svc-move-child")
            created_ids.extend([parent.id, destination.id, child.id])

            await svc.move(DatasetGroupMove(id=child.id, pid=parent.id), _user())
            moved_once = await group_repo.get_by_id(child.id)
            assert moved_once is not None
            assert moved_once.pid == parent.id
            assert moved_once.level == 1

            await svc.move(DatasetGroupMove(id=child.id, pid=destination.id), _user())
            moved_twice = await group_repo.get_by_id(child.id)

            assert moved_twice is not None
            assert moved_twice.pid == destination.id
            assert moved_twice.level == 1
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_move_to_root_sets_pid_none_and_level_zero(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            parent = await _create_group(group_repo, stamp, name_prefix="svc-root-parent")
            child = await _create_group(
                group_repo, stamp, name_prefix="svc-root-child", pid=parent.id, level=1
            )
            created_ids.extend([parent.id, child.id])

            await svc.move(DatasetGroupMove(id=child.id, pid=0), _user())
            moved = await group_repo.get_by_id(child.id)

            assert moved is not None
            assert moved.pid is None
            assert moved.level == 0
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_delete_cascade_removes_everything(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        root = await _create_group(group_repo, stamp, name_prefix="svc-delete-root")
        try:
            child = await _create_group(group_repo, stamp, name_prefix="svc-delete-child", pid=root.id, level=1)
            dataset = await _create_group(
                group_repo,
                stamp,
                name_prefix="svc-delete-dataset",
                pid=child.id,
                level=2,
                node_type="dataset",
            )
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="svc-delete-table"))
            field = await field_repo.create(
                _field_payload(stamp, group_id=dataset.id, table_id=table.id, origin_name="svc_delete_col")
            )

            await svc.delete(root.id)

            assert await group_repo.get_by_id(root.id) is None
            assert await group_repo.get_by_id(child.id) is None
            assert await group_repo.get_by_id(dataset.id) is None
            assert await table_repo.get_by_id(table.id) is None
            assert await field_repo.get_by_id(field.id) is None
        finally:
            if await group_repo.get_by_id(root.id) is not None:
                await group_repo.delete_cascade(root.id)

    async def test_get_bar_info_returns_correct_data(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="svc-bar")
            created_ids.append(group.id)

            payload = await svc.get_bar_info(group.id)

            assert payload["id"] == str(group.id)
            assert payload["pid"] is None
            assert payload["name"] == group.name
            assert payload["createBy"] == "7"
            assert payload["updateBy"] == "7"
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_get_details_returns_group_and_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="svc-details", node_type="dataset")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="svc-details-table"))
            await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_a", name="Column A")
            )
            await field_repo.create(
                _field_payload(
                    stamp,
                    group_id=group.id,
                    table_id=table.id,
                    origin_name="col_b",
                    name="Column B",
                    column_index=1,
                )
            )

            payload = cast(dict[str, Any], await svc.get_details(group.id))

            assert payload["id"] == str(group.id)
            assert payload["name"] == group.name
            assert len(payload["allFields"]) == 2
            assert payload["allFields"][0]["originName"] == "col_a"
            assert payload["allFields"][1]["originName"] == "col_b"
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_get_details_returns_fields_in_column_order(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="svc-details-order", node_type="dataset")
            created_ids.append(group.id)
            table = await table_repo.create(_table_payload(stamp, group_id=group.id, name_prefix="svc-details-order-table"))
            await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_b", column_index=1)
            )
            await field_repo.create(
                _field_payload(stamp, group_id=group.id, table_id=table.id, origin_name="col_a", column_index=0)
            )

            payload = cast(dict[str, Any], await svc.get_details(group.id))

            assert [field["originName"] for field in payload["allFields"]] == ["col_a", "col_b"]
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_per_delete_returns_true_for_existing_group(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            group = await _create_group(group_repo, stamp, name_prefix="svc-per-delete-existing")
            created_ids.append(group.id)

            assert await svc.per_delete(group.id) is True
        finally:
            for gid in reversed(created_ids):
                await group_repo.delete_cascade(gid)

    async def test_per_delete_returns_false_for_missing_group(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)

        assert await svc.per_delete(_stamp()) is False
