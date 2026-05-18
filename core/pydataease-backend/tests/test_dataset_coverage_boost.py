from __future__ import annotations

import os
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import cleanup_groups as _cleanup_groups  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.repositories.dataset_repo import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetFieldRepository,
    DatasetGroupRepository,
    DatasetTableRepository,
)
from app.repositories.dataset_sql_log_repo import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetSqlLogRepository,
)
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetGroupCreate,
    DatasetGroupUpdate,
    DatasetTableFieldRequest,
)
from app.schemas.dataset_sql_log import (  # pyright: ignore[reportImplicitRelativeImport]
    SqlLogCreateRequest,
)
from app.services.dataset_service import DatasetService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_sql_log_service import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetSqlLogService,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.getenv("DE_E2E") != "1",
        reason="Requires PostgreSQL (set DE_E2E=1)",
    ),
]


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _service(session: AsyncSession) -> DatasetService:
    return DatasetService(
        session=session,
        group_repo=DatasetGroupRepository(session),
        table_repo=DatasetTableRepository(session),
        field_repo=DatasetFieldRepository(session),
    )


def _group_payload(
    stamp: int,
    *,
    name_prefix: str,
    pid: int | None = None,
    level: int = 0,
    node_type: str = "folder",
    type_value: str | None = None,
    mode: int | None = None,
    info: object = None,
    is_cross: bool | None = None,
) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"{name_prefix}-{stamp}",
        "pid": pid,
        "level": level,
        "node_type": node_type,
        "type": type_value,
        "mode": mode,
        "info": info,
        "create_by": "7",
        "create_time": now,
        "update_by": "7",
        "last_update_time": now,
        "is_cross": is_cross,
    }


def _table_payload(stamp: int, *, group_id: int, name_prefix: str) -> dict[str, object]:
    return {
        "id": _stamp(),
        "name": f"{name_prefix}-{stamp}",
        "table_name": f"table_{name_prefix}_{stamp}",
        "datasource_id": None,
        "dataset_group_id": group_id,
        "type": "db",
        "info": None,
    }


def _field_payload(
    *,
    group_id: int,
    table_id: int | None,
    origin_name: str,
    name: str,
    dataease_name: str | None = None,
    field_short_name: str | None = None,
    group_type: str = "d",
    checked: bool = True,
    chart_id: int | None = None,
    ext_field: int = 0,
    column_index: int = 0,
) -> dict[str, object]:
    return {
        "id": _stamp(),
        "datasource_id": None,
        "dataset_table_id": table_id,
        "dataset_group_id": group_id,
        "chart_id": chart_id,
        "origin_name": origin_name,
        "name": name,
        "dataease_name": dataease_name or origin_name,
        "field_short_name": field_short_name or origin_name,
        "group_type": group_type,
        "type": "VARCHAR",
        "size": 255,
        "de_type": 0,
        "de_extract_type": 0,
        "ext_field": ext_field,
        "checked": checked,
        "column_index": column_index,
    }


class TestDatasetServiceCoverageBoost:
    async def test_save_updates_existing_dataset_and_resyncs_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            parent = await group_repo.create(_group_payload(stamp, name_prefix="save-parent"))
            destination = await group_repo.create(_group_payload(stamp, name_prefix="save-dest"))
            created_ids.extend([parent.id, destination.id])
            created = await svc.create(
                DatasetGroupCreate(
                    name=f"save-dataset-{stamp}",
                    pid=parent.id,
                    node_type="dataset",
                    type="sql",
                    mode=1,
                    info={"before": True},
                    is_cross=False,
                    all_fields=[
                        {
                            "originName": "old_col",
                            "name": "Old Column",
                            "dataeaseName": "old_col",
                            "fieldShortName": "old_col",
                            "groupType": "d",
                            "type": "VARCHAR",
                            "deType": 0,
                            "deExtractType": 0,
                            "extField": 0,
                            "checked": True,
                            "columnIndex": 0,
                        }
                    ],
                ),
                _user(),
            )
            created_ids.append(created.id)

            updated = await svc.save(
                DatasetGroupUpdate(
                    id=created.id,
                    name=f"save-dataset-updated-{stamp}",
                    pid=destination.id,
                    node_type="dataset",
                    type="excel",
                    mode=2,
                    info={"after": True, "version": stamp},
                    is_cross=True,
                    all_fields=[
                        {
                            "originName": "new_col_a",
                            "name": "New Column A",
                            "dataeaseName": "new_col_a",
                            "fieldShortName": "new_col_a",
                            "groupType": "d",
                            "type": "VARCHAR",
                            "deType": 0,
                            "deExtractType": 0,
                            "extField": 0,
                            "checked": True,
                            "columnIndex": 0,
                        },
                        {
                            "originName": "new_col_b",
                            "name": "New Column B",
                            "dataeaseName": "new_col_b",
                            "fieldShortName": "new_col_b",
                            "groupType": "q",
                            "type": "INT",
                            "deType": 1,
                            "deExtractType": 0,
                            "extField": 0,
                            "checked": False,
                            "columnIndex": 1,
                        },
                    ],
                ),
                _user(),
            )
            stored = await group_repo.get_by_id(created.id)
            fields = await field_repo.list_by_group(created.id)

            assert updated.id == created.id
            assert stored is not None
            assert stored.name == f"save-dataset-updated-{stamp}"
            assert stored.pid == destination.id
            assert stored.level == 1
            assert stored.type == "excel"
            assert stored.mode == 2
            assert stored.info == {"after": True, "version": stamp}
            assert stored.is_cross is True
            assert [field.origin_name for field in fields] == ["new_col_a", "new_col_b"]
            assert [field.name for field in fields] == ["New Column A", "New Column B"]
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_ds_details_returns_serialized_tables_and_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            dataset = await group_repo.create(
                _group_payload(stamp, name_prefix="details-dataset", node_type="dataset")
            )
            created_ids.append(dataset.id)
            table_one = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="details-a"))
            table_two = await table_repo.create(_table_payload(stamp + 1, group_id=dataset.id, name_prefix="details-b"))
            await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table_one.id,
                    origin_name="alpha",
                    name="Alpha",
                    column_index=0,
                )
            )
            await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table_one.id,
                    origin_name="beta",
                    name="Beta",
                    column_index=1,
                )
            )
            await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table_two.id,
                    origin_name="gamma",
                    name="Gamma",
                    column_index=0,
                )
            )

            payload = await svc.ds_details({"ids": [table_one.id, str(table_two.id), "bad", _stamp()]})

            assert len(payload) == 2
            first = payload[0]
            second = payload[1]
            assert first["id"] == str(table_one.id)
            assert first["datasetGroupId"] == str(dataset.id)
            assert [field["originName"] for field in cast(list[dict[str, Any]], first["fields"])] == ["alpha", "beta"]
            assert second["id"] == str(table_two.id)
            assert [field["name"] for field in cast(list[dict[str, Any]], second["fields"])] == ["Gamma"]
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_get_fields_by_dataset_group_returns_expected_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            dataset = await group_repo.create(
                _group_payload(stamp, name_prefix="get-fields-dataset", node_type="dataset")
            )
            created_ids.append(dataset.id)
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="get-fields"))
            await field_repo.create(
                _field_payload(group_id=dataset.id, table_id=table.id, origin_name="col_a", name="Column A")
            )
            await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table.id,
                    origin_name="col_b",
                    name="Column B",
                    column_index=1,
                )
            )

            payload = await svc.get_fields(DatasetTableFieldRequest(dataset_group_id=dataset.id))

            assert [field.origin_name for field in payload] == ["col_a", "col_b"]
            assert [field.dataset_group_id for field in payload] == [dataset.id, dataset.id]
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_export_dataset_returns_rows_from_payload(self, db_session: AsyncSession) -> None:
        payload = await _service(db_session).export_dataset(
            {"data": [["alpha", 1], ["beta", 2]], "ignored": True}
        )

        assert payload["rows"] == [["alpha", 1], ["beta", 2]]
        assert payload["msg"] == "Dataset export payload accepted"


class TestDatasetSqlLogServiceCoverageBoost:
    async def test_save_creates_sql_log_entry(self, db_session: AsyncSession) -> None:
        svc = DatasetSqlLogService(db_session)
        repo = DatasetSqlLogRepository(db_session)
        table_id = f"table-{_stamp()}"
        try:
            created = await svc.save(
                SqlLogCreateRequest(
                    table_id=table_id,
                    sql_snapshot="select * from metrics",
                    table_name="metrics",
                    status="SUCCESS",
                    error_msg=None,
                ),
                _user(),
            )
            rows = await repo.list_by_table_id(table_id)

            assert created.table_id == table_id
            assert created.sql_snapshot == "select * from metrics"
            assert created.status == "SUCCESS"
            assert created.create_by == "7"
            assert len(rows) == 1
            assert rows[0].id == created.id
        finally:
            await repo.delete_by_table_id(table_id)

    async def test_list_by_table_id_filters_logs(self, db_session: AsyncSession) -> None:
        svc = DatasetSqlLogService(db_session)
        table_id = f"table-{_stamp()}"
        other_table_id = f"table-{_stamp()}"
        try:
            await svc.save(
                SqlLogCreateRequest(
                    table_id=table_id, sql_snapshot="select 1", table_name="a", status="OK", error_msg=None
                ),
                _user(),
            )
            await svc.save(
                SqlLogCreateRequest(
                    table_id=table_id, sql_snapshot="select 2", table_name="a", status="FAIL", error_msg=None
                ),
                _user(),
            )
            await svc.save(
                SqlLogCreateRequest(
                    table_id=other_table_id,
                    sql_snapshot="select 3",
                    table_name="b",
                    status="OK",
                    error_msg=None,
                ),
                _user(),
            )

            rows = await svc.list_by_table_id(table_id)

            assert len(rows) == 2
            assert {row.sql_snapshot for row in rows} == {"select 1", "select 2"}
            assert {row.table_id for row in rows} == {table_id}
        finally:
            await svc.delete_by_table_id(table_id)
            await svc.delete_by_table_id(other_table_id)

    async def test_delete_by_table_id_removes_all_rows(self, db_session: AsyncSession) -> None:
        svc = DatasetSqlLogService(db_session)
        table_id = f"table-{_stamp()}"
        await svc.save(
            SqlLogCreateRequest(
                table_id=table_id, sql_snapshot="select 1", table_name="a", status="OK", error_msg=None
            ),
            _user(),
        )
        await svc.save(
            SqlLogCreateRequest(
                table_id=table_id, sql_snapshot="select 2", table_name="a", status="OK", error_msg=None
            ),
            _user(),
        )

        await svc.delete_by_table_id(table_id)

        assert await svc.list_by_table_id(table_id) == []


class TestDatasetFieldRepositoryCoverageBoost:
    async def test_save_field_update_path_overwrites_existing_row(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            dataset = await group_repo.create(
                _group_payload(stamp, name_prefix="repo-save-dataset", node_type="dataset")
            )
            created_ids.append(dataset.id)
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="repo-save"))
            field = await field_repo.create(
                _field_payload(group_id=dataset.id, table_id=table.id, origin_name="old_name", name="Old Name")
            )

            updated = await field_repo.save_field(
                {
                    "id": field.id,
                    "dataset_group_id": dataset.id,
                    "dataset_table_id": table.id,
                    "origin_name": "new_name",
                    "name": "New Name",
                    "dataease_name": "new_name",
                    "field_short_name": "new_name",
                    "group_type": "q",
                    "type": "INTEGER",
                    "de_type": 1,
                    "de_extract_type": 0,
                    "ext_field": 0,
                    "checked": False,
                    "column_index": 3,
                }
            )
            fetched = await field_repo.get_by_id(field.id)

            assert updated.id == field.id
            assert fetched is not None
            assert fetched.origin_name == "new_name"
            assert fetched.name == "New Name"
            assert fetched.checked is False
            assert fetched.column_index == 3
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_delete_by_id_removes_field(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            dataset = await group_repo.create(
                _group_payload(stamp, name_prefix="repo-delete-id-dataset", node_type="dataset")
            )
            created_ids.append(dataset.id)
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="repo-delete-id"))
            field = await field_repo.create(
                _field_payload(group_id=dataset.id, table_id=table.id, origin_name="delete_me", name="Delete Me")
            )

            await field_repo.delete_by_id(field.id)

            assert await field_repo.get_by_id(field.id) is None
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_delete_by_chart_id_removes_matching_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        chart_id = _stamp()
        other_chart_id = _stamp()
        created_ids: list[int] = []
        try:
            dataset = await group_repo.create(
                _group_payload(stamp, name_prefix="repo-delete-chart-dataset", node_type="dataset")
            )
            created_ids.append(dataset.id)
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="repo-delete-chart"))
            doomed = await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table.id,
                    origin_name="remove_a",
                    name="Remove A",
                    chart_id=chart_id,
                )
            )
            await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table.id,
                    origin_name="remove_b",
                    name="Remove B",
                    chart_id=chart_id,
                    column_index=1,
                )
            )
            keeper = await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table.id,
                    origin_name="keep_me",
                    name="Keep Me",
                    chart_id=other_chart_id,
                    column_index=2,
                )
            )

            await field_repo.delete_by_chart_id(chart_id)

            assert await field_repo.get_by_id(doomed.id) is None
            remaining = await field_repo.list_by_group(dataset.id)
            assert [field.id for field in remaining] == [keeper.id]
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_list_checked_by_group_no_chart_filter_includes_chart_fields(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            dataset = await group_repo.create(
                _group_payload(stamp, name_prefix="repo-checked-dataset", node_type="dataset")
            )
            created_ids.append(dataset.id)
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="repo-checked"))
            no_chart = await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table.id,
                    origin_name="plain_checked",
                    name="Plain Checked",
                    column_index=0,
                )
            )
            with_chart = await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table.id,
                    origin_name="chart_checked",
                    name="Chart Checked",
                    chart_id=_stamp(),
                    column_index=1,
                )
            )
            await field_repo.create(
                _field_payload(
                    group_id=dataset.id,
                    table_id=table.id,
                    origin_name="unchecked",
                    name="Unchecked",
                    checked=False,
                    column_index=2,
                )
            )

            rows = await field_repo.list_checked_by_group_no_chart_filter(dataset.id)

            assert [field.id for field in rows] == [no_chart.id, with_chart.id]
        finally:
            await _cleanup_groups(db_session, created_ids)
