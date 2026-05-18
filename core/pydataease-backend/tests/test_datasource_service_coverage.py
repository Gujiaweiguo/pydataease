# pyright: reportPrivateUsage=false, reportCallIssue=false, reportMissingTypeArgument=false

from __future__ import annotations

import base64
import os
from io import BytesIO
from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from openpyxl import Workbook
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.models.dataset import CoreDatasetGroup, CoreDatasetTable  # pyright: ignore[reportImplicitRelativeImport]
from app.models.datasource import CoreDatasource  # pyright: ignore[reportImplicitRelativeImport]
from app.models.engine import CoreDeEngine  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.datasource_repo import DatasourceRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.datasource import DatasourceCreate, DatasourceUpdate, DatasourceValidateRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.datasource_service import DatasourceService, _as_config_dict, _build_tree, _mask_passwords  # pyright: ignore[reportImplicitRelativeImport]


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _service(session: AsyncSession) -> DatasourceService:
    return DatasourceService(session=session, repository=DatasourceRepository(session))


def _unit_service() -> DatasourceService:
    return DatasourceService(
        session=cast(AsyncSession, object()),
        repository=cast(DatasourceRepository, object()),
    )


def _sheet_config(table_name: str = "Orders") -> list[dict[str, object]]:
    return [
        {
            "sheet": True,
            "sheetId": "1",
            "sheetExcelId": "1",
            "tableName": table_name,
            "deTableName": f"excel_{table_name.lower()}",
            "excelLabel": table_name,
            "fields": [
                {"name": "id", "originName": "id", "fieldType": "LONG", "deType": 2, "deExtractType": 2, "checked": True, "primaryKey": False},
                {"name": "amount", "originName": "amount", "fieldType": "DOUBLE", "deType": 3, "deExtractType": 3, "checked": True, "primaryKey": False},
            ],
            "jsonArray": [{"id": 1, "amount": 9.5}, {"id": 2, "amount": 11.0}],
            "fieldsMd5": "md5",
            "newSheet": True,
        }
    ]


def _excel_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.title = "Orders Sheet"
    sheet.append(["id", "amount", "enabled"])
    sheet.append([1, 9.5, True])
    sheet.append([2, 7.25, False])
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()


async def _cleanup(
    session: AsyncSession,
    *,
    datasource_ids: list[int],
    dataset_table_ids: list[int],
    dataset_group_ids: list[int],
    engine_ids: list[int],
) -> None:
    for table_id in dataset_table_ids:
        entity = await session.get(CoreDatasetTable, table_id)
        if entity is not None:
            await session.delete(entity)
    for group_id in dataset_group_ids:
        entity = await session.get(CoreDatasetGroup, group_id)
        if entity is not None:
            await session.delete(entity)
    for datasource_id in datasource_ids:
        entity = await session.get(CoreDatasource, datasource_id)
        if entity is not None:
            await session.delete(entity)
    for engine_id in engine_ids:
        entity = await session.get(CoreDeEngine, engine_id)
        if entity is not None:
            await session.delete(entity)
    await session.commit()


class FakeUploadFile:
    def __init__(self, filename: str, content: bytes) -> None:
        self.filename = filename
        self._content = content

    async def read(self) -> bytes:
        return self._content


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_save_update_query_get_full_and_get_simple_integration(db_session: AsyncSession) -> None:
    service = _service(db_session)
    datasource_ids: list[int] = []
    try:
        created = cast(
            dict[str, Any],
            await service.save(
                DatasourceCreate(
                    name=f" excel-source-{_stamp()} ",
                    type="Excel",
                    configuration=cast(list[object], _sheet_config()),
                    description="initial",
                    pid=0,
                    editType="0",
                    enableDataFill=False,
                ),
                _user(),
            ),
        )
        datasource_id = int(created["id"])
        datasource_ids.append(datasource_id)

        updated = cast(
            dict[str, Any],
            await service.update(
                DatasourceUpdate(id=datasource_id, name=" updated-source ", description="changed", pid=0, enableDataFill=True),
                _user(),
            ),
        )
        queried = await service.query("updated-source")
        full = cast(dict[str, Any], await service.get_full(datasource_id))
        simple = cast(dict[str, Any], await service.get_simple(datasource_id))

        assert str(created["name"]).startswith("excel-source-")
        assert updated["name"] == "updated-source"
        assert updated["description"] == "changed"
        assert updated["pid"] is None
        assert updated["enableDataFill"] is True
        assert queried[0]["id"] == datasource_id
        assert full["id"] == datasource_id
        assert simple["name"] == "updated-source"
    finally:
        await _cleanup(db_session, datasource_ids=datasource_ids, dataset_table_ids=[], dataset_group_ids=[], engine_ids=[])


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_delete_conflict_then_delete_success_integration(db_session: AsyncSession) -> None:
    service = _service(db_session)
    datasource_ids: list[int] = []
    dataset_table_ids: list[int] = []
    dataset_group_ids: list[int] = []
    now = _timestamp_ms()
    try:
        datasource = await service.repository.create(
            {
                "id": _stamp(),
                "name": f"delete-me-{_stamp()}",
                "description": None,
                "type": "Excel",
                "pid": None,
                "edit_type": None,
                "configuration": cast(list[object], _sheet_config()),
                "create_time": now,
                "update_time": now,
                "update_by": 7,
                "create_by": "7",
                "status": "Success",
                "qrtz_instance": None,
                "task_status": "WaitingForExecution",
                "enable_data_fill": False,
            }
        )
        datasource_ids.append(datasource.id)
        group = CoreDatasetGroup(
            id=_stamp(),
            name="holder",
            pid=None,
            level=0,
            node_type="folder",
            type=None,
            mode=None,
            info=None,
            create_by="7",
            create_time=now,
            qrtz_instance=None,
            sync_status=None,
            update_by="7",
            last_update_time=now,
            union_sql=None,
            is_cross=False,
        )
        db_session.add(group)
        await db_session.commit()
        dataset_group_ids.append(group.id)
        table = CoreDatasetTable(
            id=_stamp(),
            name="ref",
            table_name="ref",
            datasource_id=datasource.id,
            dataset_group_id=group.id,
            type="db",
            info=None,
            sql_variable_details=None,
        )
        db_session.add(table)
        await db_session.commit()
        dataset_table_ids.append(table.id)

        with pytest.raises(HTTPException) as exc:
            await service.delete(datasource.id)
        assert exc.value.status_code == 409

        linked = await db_session.get(CoreDatasetTable, table.id)
        if linked is not None:
            await db_session.delete(linked)
            await db_session.commit()
            dataset_table_ids.clear()

        await service.delete(datasource.id)
        assert await service.repository.get_by_id(datasource.id) is None
        datasource_ids.clear()
    finally:
        await _cleanup(db_session, datasource_ids=datasource_ids, dataset_table_ids=dataset_table_ids, dataset_group_ids=dataset_group_ids, engine_ids=[])


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_tree_move_rename_create_folder_and_latest_use_integration(db_session: AsyncSession) -> None:
    service = _service(db_session)
    datasource_ids: list[int] = []
    try:
        folder = cast(dict[str, Any], await service.create_folder(f" Folder {_stamp()} ", 0, _user()))
        folder_id = int(folder["id"])
        datasource_ids.append(folder_id)
        created = cast(
            dict[str, Any],
            await service.save(
                DatasourceCreate(
                    name=f"tree-child-{_stamp()}",
                    type="Excel",
                    configuration=cast(list[object], _sheet_config("Inventory")),
                    pid=folder_id,
                ),
                _user(),
            ),
        )
        datasource_id = int(created["id"])
        datasource_ids.append(datasource_id)

        await service.move(datasource_id, 0)
        await service.rename(datasource_id, " moved-child ")
        tree = await service.tree()
        latest = await service.latest_use()

        assert str(folder["name"]).startswith("Folder")
        assert any(node["name"] == "moved-child" for node in tree[0]["children"])
        assert "Excel" in latest
    finally:
        await _cleanup(db_session, datasource_ids=datasource_ids, dataset_table_ids=[], dataset_group_ids=[], engine_ids=[])


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_get_engine_info_check_repeat_and_validate_by_id_integration(db_session: AsyncSession) -> None:
    service = _service(db_session)
    datasource_ids: list[int] = []
    engine_ids: list[int] = []
    now = _timestamp_ms()
    try:
        engine = CoreDeEngine(
            id=_stamp(),
            name="analytics-engine",
            description=None,
            type="postgresql",
            configuration={},
            create_time=now,
            update_time=now,
            create_by="7",
            status="Success",
            enable_data_fill=False,
        )
        db_session.add(engine)
        await db_session.commit()
        engine_ids.append(engine.id)

        datasource = await service.repository.create(
            {
                "id": _stamp(),
                "name": f"repeat-source-{_stamp()}",
                "description": None,
                "type": "pg",
                "pid": None,
                "edit_type": None,
                "configuration": {"host": "127.0.0.1", "port": 5432, "database": "dataease", "schema": "public"},
                "create_time": now,
                "update_time": now,
                "update_by": 7,
                "create_by": "7",
                "status": "Success",
                "qrtz_instance": None,
                "task_status": "WaitingForExecution",
                "enable_data_fill": False,
            }
        )
        datasource_ids.append(datasource.id)

        engine_info = await service.get_engine_info()
        repeated = await service.check_repeat({"type": "pg", "configuration": {"host": "127.0.0.1", "port": 5432, "database": "dataease", "schema": "public"}})
        same_id = await service.check_repeat({"id": datasource.id, "type": "pg", "configuration": {"host": "127.0.0.1", "port": 5432, "database": "dataease", "schema": "public"}})
        validated = await service.validate_by_id(datasource.id)

        assert engine_info.configured is True
        assert engine_info.name == "analytics-engine"
        assert repeated is True
        assert same_id is False
        assert validated == {"status": "Error", "type": "pg"}
    finally:
        await _cleanup(db_session, datasource_ids=datasource_ids, dataset_table_ids=[], dataset_group_ids=[], engine_ids=engine_ids)


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_excel_datasource_tables_fields_status_preview_reparse_integration(db_session: AsyncSession) -> None:
    service = _service(db_session)
    datasource_ids: list[int] = []
    try:
        upload = cast(dict[str, Any], await service.upload_file(FakeUploadFile("orders.xlsx", _excel_bytes())))
        sheet = dict(cast(list[dict[str, Any]], upload["sheets"])[0])
        sheet["jsonArray"] = []
        created = cast(
            dict[str, Any],
            await service.save(
                DatasourceCreate(
                    name=f"excel-preview-{_stamp()}",
                    type="Excel",
                    configuration=cast(list[object], [sheet]),
                    description="excel preview",
                ),
                _user(),
            ),
        )
        datasource_id = int(created["id"])
        datasource_ids.append(datasource_id)
        table_name = str(sheet["deTableName"])

        tables = await service.get_tables(datasource_id)
        fields = await service.get_fields(datasource_id, table_name)
        status_rows = await service.get_table_status(datasource_id)
        preview = cast(dict[str, Any], await service.preview_data({"datasourceId": datasource_id, "tableName": table_name}))
        preview_data = cast(dict[str, Any], preview["data"])

        assert [table.name for table in tables] == [table_name]
        assert [field.name for field in fields] == ["id", "amount", "enabled"]
        assert status_rows[0]["tableName"] == table_name
        assert cast(list[dict[str, Any]], preview_data["fields"])[0]["name"] == "id"
        assert len(cast(list[dict[str, Any]], preview_data["data"])) == 2
        assert cast(list[dict[str, Any]], preview_data["data"])[0]["id"] == 1
    finally:
        await _cleanup(db_session, datasource_ids=datasource_ids, dataset_table_ids=[], dataset_group_ids=[], engine_ids=[])


@pytest.mark.asyncio
async def test_get_schemas_from_config_returns_names() -> None:
    service = _unit_service()

    class FakeConnection:
        closed = False

        async def fetch(self, query: str, *args: Any) -> list[dict[str, object]]:
            assert "information_schema.schemata" in query
            return [{"schema_name": "alpha"}, {"schema_name": "beta"}]

        async def close(self) -> None:
            self.closed = True

    connection = FakeConnection()

    async def fake_open(configuration: dict[str, object], ds_type: str | None = None) -> FakeConnection:
        assert configuration["host"] == "db"
        assert ds_type == "pg"
        return connection

    service._open_connection = fake_open  # type: ignore[method-assign]

    assert await service.get_schemas_from_config({"host": "db"}, "unknown") == []
    assert await service.get_schemas_from_config({"host": "db"}, "pg") == ["alpha", "beta"]
    assert connection.closed is True


@pytest.mark.asyncio
async def test_validate_handles_file_supported_and_unsupported_types() -> None:
    service = _unit_service()
    calls: list[tuple[str, dict[str, object]]] = []

    async def fake_validate(ds_type: str, configuration: dict[str, object]) -> None:
        calls.append((ds_type, configuration))

    service._validate_connection = fake_validate  # type: ignore[method-assign]

    excel = await service.validate(DatasourceValidateRequest(name="f", type="Excel", configuration=[]))
    pg = await service.validate(DatasourceValidateRequest(name="p", type="pg", configuration={"host": "db", "port": 5432}))

    assert excel.success is True
    assert pg.datasource_type == "pg"
    assert calls == [("pg", {"host": "db", "port": 5432})]

    with pytest.raises(HTTPException) as exc:
        await service.validate(DatasourceValidateRequest(name="bad", type="oracle", configuration={}))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_open_connection_wraps_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _unit_service()

    async def raise_value(ds_type: str, configuration: dict[str, object]) -> None:
        raise ValueError("bad config")

    monkeypatch.setattr("app.services.datasource_service.open_connection", raise_value)
    with pytest.raises(HTTPException) as exc:
        await service._open_connection({"host": "db"}, "pg")
    assert exc.value.detail == "bad config"

    async def raise_runtime(ds_type: str, configuration: dict[str, object]) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr("app.services.datasource_service.open_connection", raise_runtime)
    with pytest.raises(HTTPException) as exc2:
        await service._open_connection({"host": "db"}, "pg")
    assert "Connection failed: boom" in str(exc2.value.detail)


@pytest.mark.asyncio
async def test_upload_file_and_load_remote_file() -> None:
    service = _unit_service()
    csv_bytes = b"id,amount\n1,10\n2,11\n"
    uploaded = cast(dict[str, Any], await service.upload_file(FakeUploadFile("orders.csv", csv_bytes)))

    async def fake_download(url: str, username: str, password: str) -> tuple[bytes, str]:
        assert url == "https://example.com/data.csv"
        assert username == "demo-user"
        assert password == "demo-pass"
        return csv_bytes, "remote.csv"

    service._download_remote_file = fake_download  # type: ignore[method-assign]
    remote = cast(
        dict[str, Any],
        await service.load_remote_file(
            {
                "url": "https://example.com/data.csv",
                "userName": base64.b64encode(b"demo-user").decode(),
                "passwd": base64.b64encode(b"demo-pass").decode(),
            }
        ),
    )

    assert uploaded["fileName"] == "orders.csv"
    assert cast(list[dict[str, Any]], cast(list[dict[str, Any]], uploaded["sheets"])[0]["jsonArray"])[0]["id"] == "1"
    assert remote["fileName"] == "remote.csv"


def test_parse_uploaded_excel_metadata() -> None:
    service = _unit_service()
    parsed = cast(dict[str, Any], service._parse_uploaded_file(_excel_bytes(), "orders.xlsx"))
    sheet = cast(list[dict[str, Any]], parsed["sheets"])[0]

    assert parsed["excelLabel"] == "orders.xlsx"
    assert sheet["sheet"] is True
    assert str(sheet["deTableName"]).startswith("excel_orders_sheet_")
    assert cast(list[dict[str, Any]], sheet["fields"])[0]["fieldType"] == "LONG"
    assert len(cast(list[dict[str, Any]], sheet["jsonArray"])) == 2
    assert "_rawFileBase64" in sheet


def test_decorate_response_for_api_and_excelremote() -> None:
    service = _unit_service()
    now = _timestamp_ms()
    api_entity = CoreDatasource(
        id=_stamp(),
        name="api-ds",
        description=None,
        type="API-order",
        pid=None,
        edit_type=None,
        configuration=cast(list[object], [{"name": "orders", "type": "table"}, {"name": "runtime", "type": "params"}]),
        create_time=now,
        update_time=now,
        update_by=7,
        create_by="7",
        status="Success",
        qrtz_instance=None,
        task_status="WaitingForExecution",
        enable_data_fill=False,
    )
    excel_entity = CoreDatasource(
        id=_stamp(),
        name="excel-remote",
        description=None,
        type="ExcelRemote",
        pid=None,
        edit_type=None,
        configuration={"sheets": cast(list[object], _sheet_config()), "syncSetting": {"syncRate": "SIMPLE_CRON"}},
        create_time=now,
        update_time=now,
        update_by=7,
        create_by="7",
        status="Success",
        qrtz_instance=None,
        task_status="WaitingForExecution",
        enable_data_fill=False,
    )

    api_data = service._decorate_datasource_response(api_entity)
    excel_data = service._decorate_datasource_response(excel_entity)

    assert api_data["configuration"] == {}
    assert api_data["apiConfigurationStr"] == [{"name": "orders", "type": "table"}]
    assert api_data["paramsStr"] == [{"name": "runtime", "type": "params"}]
    assert cast(dict[str, Any], api_data["syncSetting"])["syncRate"] == "SIMPLE_CRON"
    assert excel_data["syncSetting"] == {"syncRate": "SIMPLE_CRON"}
    assert excel_data["fileName"] == "excel-remote.xlsx"


def test_configuration_split_sync_default_helpers() -> None:
    service = _unit_service()
    persisted = cast(dict[str, Any], service._persistable_configuration("ExcelRemote", cast(list[object], _sheet_config()), {"syncRate": "SIMPLE_CRON"}))
    extracted = service._extract_sync_setting(persisted)
    api_items, param_items = service._split_api_configuration([{"name": "orders", "type": "table"}, {"name": "runtime", "type": "params"}])

    assert cast(list[dict[str, Any]], persisted["sheets"])[0]["tableName"] == "Orders"
    assert extracted == {"syncRate": "SIMPLE_CRON"}
    assert api_items == [{"name": "orders", "type": "table"}]
    assert param_items == [{"name": "runtime", "type": "params"}]
    assert service._default_sync_setting()["cron"] == "0 0/1 * * * ? *"


@pytest.mark.asyncio
async def test_probe_status_and_type_helpers() -> None:
    service = _unit_service()

    async def ok_validate(ds_type: str, configuration: dict[str, object]) -> None:
        return None

    async def bad_validate(ds_type: str, configuration: dict[str, object]) -> None:
        raise RuntimeError("nope")

    service._validate_connection = ok_validate  # type: ignore[method-assign]
    assert await service._probe_status("Excel", []) == "Success"
    assert await service._probe_status("pg", {"host": "db"}) == "Success"

    service._validate_connection = bad_validate  # type: ignore[method-assign]
    assert await service._probe_status("pg", {"host": "db"}) == "Error"
    assert service._schema_name({"schema": "analytics"}, "postgresql") == "analytics"
    assert service._schema_name({"database": "warehouse"}, "mysql") == "warehouse"
    assert service._field_de_type("bigint") == 2
    assert service._field_de_type("numeric") == 3
    assert service._field_de_type("date") == 1
    assert service._field_de_type("varchar") == 0


def test_build_tree_mask_passwords_and_as_config_dict() -> None:
    tree = _build_tree([{"id": "1", "pid": "0", "name": "root-child"}, {"id": "2", "pid": "1", "name": "grandchild"}])
    config: dict[str, object] = {"password": "secret", "nested": {"accessKey": "abc", "safe": "ok"}}
    _mask_passwords(config)

    assert tree[0]["children"][0]["name"] == "grandchild"
    assert config["password"] == "******"
    assert cast(dict[str, Any], config["nested"])["accessKey"] == "******"
    assert _as_config_dict({"host": "db"}) == {"host": "db"}

    with pytest.raises(HTTPException) as exc:
        _as_config_dict([])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_misc_noop_and_field_helpers() -> None:
    service = _unit_service()
    preview_field = service._excel_preview_field({"name": "amount", "fieldType": "DOUBLE", "deType": 3})
    excel_field = service._excel_datasource_field({"originName": "id", "fieldType": "LONG", "deType": 2, "primaryKey": True})
    db_field = service._db_datasource_field({"column_name": "created_at", "data_type": "TIMESTAMP", "is_nullable": "NO"})

    assert await service.sync_api_table({"id": 1}) is None
    assert await service.sync_api_datasource({"id": 1}) is None
    assert await service.list_sync_record(1, 2, 10) == {"records": [], "total": 0, "page": 2, "pageSize": 10}
    assert await service.check_api_datasource({"id": 1}) == {"jsonFields": [], "fields": [], "data": []}
    assert preview_field == {"name": "amount", "originName": "amount", "deType": 3, "fieldType": "DOUBLE"}
    assert excel_field.name == "id"
    assert excel_field.nullable is False
    assert db_field.de_type == 1
