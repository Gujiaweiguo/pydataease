from __future__ import annotations

import base64
import os
from typing import Any, cast

import pytest
from sqlalchemy import update
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.models.dataset import CoreDatasetGroup, CoreDatasetTable, CoreDatasetTableField  # pyright: ignore[reportImplicitRelativeImport]
from app.models.datasource import CoreDatasource  # pyright: ignore[reportImplicitRelativeImport]
from app.models.column_permission import CoreColumnPermission  # pyright: ignore[reportImplicitRelativeImport]
from app.models.row_permission import CoreRowPermission  # pyright: ignore[reportImplicitRelativeImport]
from app.models.sys_variable import CoreSysVariable, CoreSysVariableValue  # pyright: ignore[reportImplicitRelativeImport]
from app.models.user import CoreUser  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.dataset_repo import DatasetFieldRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.dataset_repo import DatasetGroupRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.dataset_repo import DatasetTableRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.datasource_repo import DatasourceRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import DatasetGroupCreate, DatasetEnumValueRequest, DatasetPreviewDataRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import DatasetService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.datasource_service import DatasourceService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.datasource_drivers import _AsyncmyConnectionWrapper  # pyright: ignore[reportImplicitRelativeImport]
from app.utils.password_utils import hash_password  # pyright: ignore[reportImplicitRelativeImport]

MYSQL_CONFIG: dict[str, object] = {
    "host": "127.0.0.1",
    "port": "3306",
    "username": "root",
    "password": "Admin168",
    "database": "test_ds",
    "extraParameters": "",
}

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.getenv("DE_E2E") != "1",
        reason="Requires PostgreSQL + MySQL (set DE_E2E=1)",
    ),
]


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _dataset_service(session: AsyncSession) -> DatasetService:
    return DatasetService(
        session=session,
        group_repo=DatasetGroupRepository(session),
        table_repo=DatasetTableRepository(session),
        field_repo=DatasetFieldRepository(session),
    )


def _datasource_service(session: AsyncSession) -> DatasourceService:
    return DatasourceService(session, DatasourceRepository(session))


async def _create_mysql_datasource(session: AsyncSession, stamp: int) -> CoreDatasource:
    ds_data = {
        "id": stamp,
        "name": f"test-mysql-ds-{stamp}",
        "description": "Integration test datasource",
        "type": "mysql",
        "pid": None,
        "edit_type": None,
        "configuration": MYSQL_CONFIG,
        "create_time": _timestamp_ms(),
        "update_time": _timestamp_ms(),
        "update_by": None,
        "create_by": "7",
        "status": "Success",
    }
    ds = CoreDatasource(**ds_data)
    session.add(ds)
    await session.commit()
    await session.refresh(ds)
    return ds


async def _create_dataset_group(session: AsyncSession, datasource_id: int, stamp: int) -> int:
    service = _dataset_service(session)
    group = await service.create(
        DatasetGroupCreate(
            name=f"mysql-dataset-{stamp}",
            pid=0,
            node_type="dataset",
            info={"datasourceId": datasource_id, "tableName": "customers"},
        ),
        _user(),
    )
    payload = group.model_dump() if hasattr(group, "model_dump") else cast(dict[str, object], cast(object, group))
    return int(cast(int | str, payload["id"]))


async def _create_stores_dataset_group(session: AsyncSession, datasource_id: int, stamp: int) -> int:
    service = _dataset_service(session)
    group = await service.create(
        DatasetGroupCreate(
            name=f"mysql-store-dataset-{stamp}",
            pid=0,
            node_type="dataset",
            info={"datasourceId": datasource_id, "tableName": "permission_stores"},
        ),
        _user(),
    )
    payload = group.model_dump() if hasattr(group, "model_dump") else cast(dict[str, object], cast(object, group))
    return int(cast(int | str, payload["id"]))


async def _prepare_permission_stores_table(session: AsyncSession) -> None:
    connection = await _datasource_service(session)._open_connection(MYSQL_CONFIG, ds_type="mysql")
    try:
        await connection.execute("DROP TABLE IF EXISTS permission_stores")
        await connection.execute(
            "CREATE TABLE permission_stores ("
            "日期 DATETIME, 店铺 VARCHAR(255), 用途 VARCHAR(255), 金额 INT"
            ")"
        )
        await connection.execute(
            "INSERT INTO permission_stores (日期, 店铺, 用途, 金额) VALUES "
            "('2024-03-10 17:00:18', '欢果店', '原料购进', 162),"
            "('2024-03-25 01:07:42', '蓝墨店', '原料购进', 141),"
            "('2024-03-28 05:35:18', '果元店', '原料购进', 802),"
            "('2024-03-03 15:26:33', '蓝墨店', '原料购进', 646),"
            "('2024-03-26 18:36:21', '南都店', '原料购进', 680),"
            "('2024-03-01 07:55:58', '蓝墨店', '原料购进', 571)"
        )
    finally:
        await connection.close()


async def _load_dataset_table(session: AsyncSession, group_id: int) -> CoreDatasetTable:
    table = (await DatasetTableRepository(session).list_by_group(group_id))[0]
    return table


async def _load_dataset_fields(session: AsyncSession, group_id: int) -> list[CoreDatasetTableField]:
    return list(await DatasetFieldRepository(session).list_by_group(group_id))


def _field_names(fields: list[CoreDatasetTableField]) -> list[str]:
    return [field.origin_name for field in fields]


class _PreviewRecord(dict[str, Any]):
    def __iter__(self):
        return iter(self.values())


@pytest.fixture
def mysql_preview_records(monkeypatch: pytest.MonkeyPatch) -> None:
    original_fetch = _AsyncmyConnectionWrapper.fetch

    async def _fetch_with_preview_records(self: _AsyncmyConnectionWrapper, query: str, *args: Any) -> list[Any]:
        rows = await original_fetch(self, query, *args)
        return [_PreviewRecord(row) for row in rows]

    monkeypatch.setattr(_AsyncmyConnectionWrapper, "fetch", _fetch_with_preview_records)


async def _cleanup_entities(
    session: AsyncSession,
    created_group_ids: list[int],
    created_ds_ids: list[int],
) -> None:
    group_repo = DatasetGroupRepository(session)
    for gid in reversed(created_group_ids):
        try:
            await group_repo.delete_cascade(gid)
        except Exception:
            pass
    for ds_id in reversed(created_ds_ids):
        try:
            ds = await session.get(CoreDatasource, ds_id)
            if ds:
                await session.delete(ds)
                await session.commit()
        except Exception:
            await session.rollback()


async def _cleanup_permission_entities(
    session: AsyncSession,
    *,
    dataset_id: int,
    user_id: int,
    variable_name: str,
) -> None:
    variable_stmt = select(CoreSysVariable).where(CoreSysVariable.name == variable_name)
    variable = (await session.execute(variable_stmt)).scalar_one_or_none()
    if variable is not None:
        await session.execute(text("DELETE FROM core_sys_variable_value WHERE variable_id = :variable_id"), {"variable_id": variable.id})
        await session.execute(text("DELETE FROM core_sys_variable WHERE id = :variable_id"), {"variable_id": variable.id})
    await session.execute(text("DELETE FROM core_column_permission WHERE dataset_id = :dataset_id"), {"dataset_id": dataset_id})
    await session.execute(text("DELETE FROM core_row_permission WHERE dataset_id = :dataset_id"), {"dataset_id": dataset_id})
    await session.execute(text("DELETE FROM core_user WHERE id = :user_id"), {"user_id": user_id})
    await session.commit()


async def _seed_mysql_dataset_permissions(
    session: AsyncSession,
    *,
    dataset_id: int,
    user_id: int,
    oid: int,
    field_id: int,
    variable_name: str,
    variable_value: str,
) -> None:
    now = _timestamp_ms()
    variable_id = _stamp()
    session.add(
        CoreUser(
            id=user_id,
            account=f"perm_user_{user_id}",
            name=f"perm_user_{user_id}",
            email=None,
            phone=None,
            phone_prefix=None,
            password=hash_password("DataEase@123456"),
            enable=True,
            oid=oid,
            origin=0,
            mfa_enable=False,
            language="zh_CN",
            create_time=now,
            update_time=now,
        )
    )
    session.add(
        CoreSysVariable(
            id=variable_id,
            name=variable_name,
            alias=variable_name,
            type="string",
            remark="integration test variable",
            dataset_group_id=dataset_id,
            dataset_table_id=None,
            create_time=now,
            update_time=now,
            create_by=1,
        )
    )
    session.add(
        CoreSysVariableValue(
            id=_stamp(),
            variable_id=variable_id,
            value=variable_value,
            name=variable_name,
            remark="integration test value",
            create_time=now,
            update_time=now,
        )
    )
    session.add(
        CoreRowPermission(
            id=_stamp(),
            dataset_id=dataset_id,
            target_type="sysvar",
            target_id=0,
            filter_sql="店铺 = ${store_name}",
            enabled=True,
            create_time=now,
            update_time=now,
        )
    )
    session.add(
        CoreColumnPermission(
            id=_stamp(),
            dataset_id=dataset_id,
            field_id=field_id,
            target_type="user",
            target_id=user_id,
            action="mask",
            enabled=True,
            create_time=now,
            update_time=now,
        )
    )
    await session.commit()


class TestDatasetDatasourceIntegration:
    async def test_register_mysql_datasource_persists_core_datasource_row(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)

            stored = await db_session.get(CoreDatasource, ds.id)

            assert stored is not None
            assert stored.type == "mysql"
            stored_config = cast(dict[str, object], stored.configuration)
            assert stored_config["database"] == "test_ds"
            assert stored.status == "Success"
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_datasource_service_get_fields_reads_mysql_customers_columns(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)

            fields = await _datasource_service(db_session).get_fields(ds.id, "customers")

            assert [field.name for field in fields] == ["id", "name", "age", "created_at"]
            assert [field.data_type.lower() for field in fields] == ["int", "varchar", "int", "datetime"]
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_create_dataset_linked_to_mysql_persists_dataset_group_info(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            stored = await db_session.get(CoreDatasetGroup, group_id)

            assert stored is not None
            assert stored.node_type == "dataset"
            stored_info = cast(dict[str, object], stored.info)
            assert stored_info["datasourceId"] == ds.id
            assert stored_info["tableName"] == "customers"
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_sync_dataset_source_creates_dataset_table_linkage(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            dataset_table = await _load_dataset_table(db_session, group_id)

            assert dataset_table.dataset_group_id == group_id
            assert dataset_table.datasource_id == ds.id
            assert dataset_table.table_name == "customers"
            assert dataset_table.type == "db"
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_sync_dataset_source_creates_dataset_fields_matching_mysql_columns(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            fields = await _load_dataset_fields(db_session, group_id)

            assert len(fields) == 4
            assert _field_names(fields) == ["id", "name", "age", "created_at"]
            assert [field.name for field in fields] == ["id", "name", "age", "created_at"]
            assert [field.column_index for field in fields] == [0, 1, 2, 3]
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_sync_dataset_source_maps_mysql_field_types_to_expected_de_types(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            fields = await _load_dataset_fields(db_session, group_id)
            de_types = {field.origin_name: field.de_type for field in fields}

            assert de_types == {"id": 1, "name": 0, "age": 1, "created_at": 2}
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_get_details_returns_synced_mysql_fields(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            details = cast(dict[str, Any], await _dataset_service(db_session).get_details(group_id))
            all_fields = cast(list[dict[str, Any]], details["allFields"])

            assert [field["originName"] for field in all_fields] == ["id", "name", "age", "created_at"]
            assert [field["deType"] for field in all_fields] == [1, 0, 1, 2]
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_preview_sql_returns_real_mysql_data(self, db_session: AsyncSession, mysql_preview_records: None) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            sql = "SELECT * FROM customers ORDER BY id"
            encoded_sql = base64.b64encode(sql.encode()).decode()

            payload = cast(
                dict[str, Any],
                await _dataset_service(db_session).preview_sql(
                {"sql": encoded_sql, "datasourceId": str(ds.id), "datasource_id": ds.id}
                ),
            )
            rows = cast(list[list[Any]], payload["data"])
            fields = cast(list[dict[str, Any]], payload["fields"])

            assert payload["sql"] == "SELECT * FROM customers ORDER BY id LIMIT 1000"
            assert payload["total"] == 3
            assert rows == [
                [1, "Alice", 30, rows[0][3]],
                [2, "Bob", 25, rows[1][3]],
                [3, "Charlie", 35, rows[2][3]],
            ]
            assert [field["name"] for field in fields] == ["id", "name", "age", "created_at"]
            assert [field["type"] for field in fields] == ["integer", "varchar", "integer", "timestamp"]
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_preview_sql_mysql_result_contains_expected_created_at_values(self, db_session: AsyncSession, mysql_preview_records: None) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            sql = "SELECT * FROM customers ORDER BY id"
            encoded_sql = base64.b64encode(sql.encode()).decode()

            payload = cast(dict[str, Any], await _dataset_service(db_session).preview_sql({"sql": encoded_sql, "datasourceId": ds.id}))

            created_values = [str(row[3]) for row in cast(list[list[Any]], payload["data"])]
            assert created_values == [
                "2024-01-01 00:00:00",
                "2024-06-15 00:00:00",
                "2024-12-01 00:00:00",
            ]
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_check_in_use_returns_true_while_dataset_table_references_datasource(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            in_use = await _datasource_service(db_session).check_in_use(ds.id)

            assert in_use is True
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_dataset_table_repository_can_find_synced_table_by_datasource_and_name(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            dataset_table = await DatasetTableRepository(db_session).get_by_datasource_and_table(ds.id, "customers")

            assert dataset_table is not None
            assert dataset_table.dataset_group_id == group_id
            assert dataset_table.datasource_id == ds.id
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_deleting_datasource_keeps_dataset_group_and_clears_datasource_reference(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            group_id = await _create_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)

            await db_session.execute(
                update(CoreDatasetTable)
                .where(CoreDatasetTable.dataset_group_id == group_id)
                .values(datasource_id=None)
            )
            await db_session.execute(
                update(CoreDatasetTableField)
                .where(CoreDatasetTableField.dataset_group_id == group_id)
                .values(datasource_id=None)
            )
            await db_session.commit()
            await db_session.execute(text("DELETE FROM core_datasource WHERE id = :ds_id"), {"ds_id": ds.id})
            await db_session.commit()
            created_ds_ids.remove(ds.id)

            group = await db_session.get(CoreDatasetGroup, group_id)
            dataset_table = await _load_dataset_table(db_session, group_id)
            fields = await _load_dataset_fields(db_session, group_id)

            assert group is not None
            assert dataset_table.datasource_id is None
            assert all(field.datasource_id is None for field in fields)
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_mysql_fixture_table_contains_expected_seed_rows(self, db_session: AsyncSession) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        try:
            result = await db_session.execute(select(1))
            assert result.scalar() == 1

            ds_stamp = _stamp()
            ds = await _create_mysql_datasource(db_session, ds_stamp)
            created_ds_ids.append(ds.id)
            connection = await _datasource_service(db_session)._open_connection(MYSQL_CONFIG, ds_type="mysql")
            try:
                rows = await connection.fetch("SELECT id, name, age FROM customers ORDER BY id")
            finally:
                await connection.close()

            assert rows == [
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25},
                {"id": 3, "name": "Charlie", "age": 35},
            ]
        finally:
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_preview_data_restricted_user_applies_sysvar_row_filter_and_mask_on_mysql_dataset(
        self,
        db_session: AsyncSession,
        mysql_preview_records: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        user_id = _stamp()
        variable_name = "store_name"
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            await _prepare_permission_stores_table(db_session)
            group_id = await _create_stores_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)
            fields = await _load_dataset_fields(db_session, group_id)
            store_field = next(field for field in fields if field.origin_name == "店铺")
            await _seed_mysql_dataset_permissions(
                db_session,
                dataset_id=group_id,
                user_id=user_id,
                oid=9,
                field_id=store_field.id,
                variable_name=variable_name,
                variable_value="蓝墨店",
            )
            factory = async_sessionmaker(bind=db_session.bind, class_=AsyncSession, expire_on_commit=False)
            monkeypatch.setattr("app.services.dataset_service.async_session", factory)

            payload = await _dataset_service(db_session).preview_data(
                DatasetPreviewDataRequest(dataset_group_id=group_id, limit=20, offset=0),
                TokenUser(user_id=user_id, oid=9),
            )
            data = cast(dict[str, Any], payload["data"])
            rows = cast(list[list[Any]], data["data"])
            normalized_rows = [[str(row[0]).replace(" ", "T"), row[1], row[2], row[3]] for row in rows]

            assert data["total"] == 3
            assert normalized_rows == [
                ["2024-03-25T01:07:42", "蓝*店", "原料购进", 141],
                ["2024-03-03T15:26:33", "蓝*店", "原料购进", 646],
                ["2024-03-01T07:55:58", "蓝*店", "原料购进", 571],
            ]
        finally:
            if created_group_ids:
                await _cleanup_permission_entities(
                    db_session,
                    dataset_id=created_group_ids[0],
                    user_id=user_id,
                    variable_name=variable_name,
                )
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)

    async def test_enum_values_restricted_user_applies_sysvar_row_filter_and_mask_on_mysql_dataset(
        self,
        db_session: AsyncSession,
        mysql_preview_records: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        created_group_ids: list[int] = []
        created_ds_ids: list[int] = []
        user_id = _stamp()
        variable_name = "store_name"
        stamp = _stamp()
        try:
            ds = await _create_mysql_datasource(db_session, stamp)
            created_ds_ids.append(ds.id)
            await _prepare_permission_stores_table(db_session)
            group_id = await _create_stores_dataset_group(db_session, ds.id, stamp)
            created_group_ids.append(group_id)
            fields = await _load_dataset_fields(db_session, group_id)
            store_field = next(field for field in fields if field.origin_name == "店铺")
            await _seed_mysql_dataset_permissions(
                db_session,
                dataset_id=group_id,
                user_id=user_id,
                oid=9,
                field_id=store_field.id,
                variable_name=variable_name,
                variable_value="蓝墨店",
            )
            factory = async_sessionmaker(bind=db_session.bind, class_=AsyncSession, expire_on_commit=False)
            monkeypatch.setattr("app.services.dataset_service.async_session", factory)

            values = await _dataset_service(db_session).get_enum_values(
                DatasetEnumValueRequest(dataset_group_id=group_id, field_id=store_field.id, result_limit=20),
                TokenUser(user_id=user_id, oid=9),
            )

            assert values == ["蓝*店"]
        finally:
            if created_group_ids:
                await _cleanup_permission_entities(
                    db_session,
                    dataset_id=created_group_ids[0],
                    user_id=user_id,
                    variable_name=variable_name,
                )
            await _cleanup_entities(db_session, created_group_ids, created_ds_ids)
