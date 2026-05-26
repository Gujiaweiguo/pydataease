# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false

from __future__ import annotations

import os
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.models.chart import CoreChartView  # pyright: ignore[reportImplicitRelativeImport]
from app.models.dataset import CoreDatasetGroup, CoreDatasetTable, CoreDatasetTableField  # pyright: ignore[reportImplicitRelativeImport]
from app.models.datasource import CoreDatasource  # pyright: ignore[reportImplicitRelativeImport]
from app.models.visualization import DataVisualizationInfo  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.chart_repo import ChartRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.dataset_repo import DatasetFieldRepository, DatasetGroupRepository, DatasetTableRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.datasource_repo import DatasourceRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.chart import ChartDataRequest, ChartSaveRequest, ChartUpdateRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.chart_service import ChartService  # pyright: ignore[reportImplicitRelativeImport]


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _service(session: AsyncSession) -> ChartService:
    return ChartService(session)


def _unit_service() -> ChartService:
    return ChartService(cast(AsyncSession, cast(object, SimpleNamespace())))


def _viz_payload(stamp: int, *, name: str = "scene") -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"{name}-{stamp}",
        "pid": None,
        "org_id": None,
        "level": 0,
        "node_type": "leaf",
        "type": "panel",
        "canvas_style_data": None,
        "component_data": None,
        "mobile_layout": False,
        "status": 0,
        "self_watermark_status": 0,
        "sort": 0,
        "create_time": now,
        "create_by": "7",
        "update_time": now,
        "update_by": "7",
        "remark": None,
        "source": None,
        "delete_flag": False,
        "delete_time": None,
        "delete_by": None,
        "version": 1,
        "content_id": None,
        "check_version": None,
    }


def _chart_payload(stamp: int, *, scene_id: int, table_id: int | None = None, title: str = "chart") -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "title": f"{title}-{stamp}",
        "scene_id": scene_id,
        "table_id": table_id,
        "type": "bar",
        "render": "antv",
        "result_count": 20,
        "result_mode": "custom",
        "x_axis": [{"name": "region", "dataeaseName": "region"}],
        "x_axis_ext": None,
        "y_axis": [{"name": "sales", "dataeaseName": "sales", "summary": "sum"}],
        "y_axis_ext": None,
        "ext_stack": None,
        "ext_bubble": None,
        "ext_label": None,
        "ext_tooltip": None,
        "custom_attr": None,
        "custom_style": None,
        "custom_filter": None,
        "drill_fields": None,
        "senior": None,
        "create_by": "7",
        "create_time": now,
        "update_time": now,
        "snapshot": None,
        "style_priority": None,
        "chart_type": "bar",
        "is_plugin": False,
        "data_from": None,
        "view_fields": None,
        "refresh_view_enable": None,
        "refresh_unit": None,
        "refresh_time": None,
        "linkage_active": None,
        "jump_active": None,
        "copy_from": None,
        "copy_id": None,
        "aggregate": None,
        "flow_map_start_name": None,
        "flow_map_end_name": None,
        "ext_color": None,
        "custom_attr_mobile": None,
        "custom_style_mobile": None,
        "sort_priority": None,
    }


def _group_payload(stamp: int, *, name: str = "group", union_sql: str | None = None, info: object = None) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"{name}-{stamp}",
        "pid": None,
        "level": 0,
        "node_type": "dataset",
        "type": "sql",
        "mode": 1,
        "info": info,
        "create_by": "7",
        "create_time": now,
        "qrtz_instance": None,
        "sync_status": None,
        "update_by": "7",
        "last_update_time": now,
        "union_sql": union_sql,
        "is_cross": False,
    }


def _table_payload(stamp: int, *, group_id: int, datasource_id: int | None = None, table_name: str = "orders") -> dict[str, object]:
    return {
        "id": _stamp(),
        "name": f"table-{stamp}",
        "table_name": table_name,
        "datasource_id": datasource_id,
        "dataset_group_id": group_id,
        "type": "db",
        "info": None,
        "sql_variable_details": None,
    }


def _field_payload(*, group_id: int, table_id: int, origin_name: str, name: str, index: int) -> dict[str, object]:
    return {
        "id": _stamp(),
        "datasource_id": None,
        "dataset_table_id": table_id,
        "dataset_group_id": group_id,
        "chart_id": None,
        "origin_name": origin_name,
        "name": name,
        "description": None,
        "dataease_name": origin_name,
        "field_short_name": origin_name,
        "group_list": None,
        "other_group": None,
        "group_type": "d",
        "type": "VARCHAR",
        "size": 255,
        "de_type": 0,
        "de_extract_type": 0,
        "ext_field": 0,
        "checked": True,
        "column_index": index,
        "last_sync_time": None,
        "accuracy": None,
        "date_format": None,
        "date_format_type": None,
        "params": None,
        "order_checked": None,
    }


def _datasource_payload(stamp: int) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"ds-{stamp}",
        "description": None,
        "type": "PostgreSQL",
        "pid": None,
        "edit_type": None,
        "configuration": {"host": "127.0.0.1", "port": 5432, "database": "dataease"},
        "create_time": now,
        "update_time": now,
        "update_by": 7,
        "create_by": "7",
        "status": "Success",
        "qrtz_instance": None,
        "task_status": "WaitingForExecution",
        "enable_data_fill": False,
    }


async def _cleanup_entities(
    session: AsyncSession,
    *,
    chart_ids: list[int],
    field_ids: list[int],
    table_ids: list[int],
    group_ids: list[int],
    datasource_ids: list[int],
    visualization_ids: list[int],
) -> None:
    for field_id in field_ids:
        entity = await session.get(CoreDatasetTableField, field_id)
        if entity is not None:
            await session.delete(entity)
    await session.commit()
    for chart_id in chart_ids:
        entity = await session.get(CoreChartView, chart_id)
        if entity is not None:
            await session.delete(entity)
    await session.commit()
    for table_id in table_ids:
        entity = await session.get(CoreDatasetTable, table_id)
        if entity is not None:
            await session.delete(entity)
    await session.commit()
    for group_id in group_ids:
        entity = await session.get(CoreDatasetGroup, group_id)
        if entity is not None:
            await session.delete(entity)
    await session.commit()
    for datasource_id in datasource_ids:
        entity = await session.get(CoreDatasource, datasource_id)
        if entity is not None:
            await session.delete(entity)
    await session.commit()
    for visualization_id in visualization_ids:
        entity = await session.get(DataVisualizationInfo, visualization_id)
        if entity is not None:
            await session.delete(entity)
    await session.commit()


class FakeRecord:
    def __init__(self, **data: object) -> None:
        self._data = data

    def keys(self):
        return self._data.keys()

    def __iter__(self):
        return iter(self._data.values())


class FakeConnection:
    def __init__(self, records: list[FakeRecord]) -> None:
        self.records = records
        self.closed = False
        self.sql: str | None = None

    async def fetch(self, sql: str) -> list[FakeRecord]:
        self.sql = sql
        return self.records

    async def close(self) -> None:
        self.closed = True


def test_axis_merge_helpers_and_identifier_validation() -> None:
    service = _unit_service()
    payload = ChartDataRequest(
        id=1,
        x_axis=[{"name": "region"}],
        x_axis_ext=[{"name": "month"}],
        y_axis=[{"name": "sales"}],
        y_axis_ext=[{"name": "profit"}],
        ext_bubble=[{"name": "size"}],
        ext_label=[{"name": "label"}],
        ext_stack=[{"name": "stack"}],
        ext_tooltip=[{"name": "tip"}],
        ext_color=[{"name": "color"}],
        view_fields=None,
        fields=None,
    )

    merged = service._merge_axis_fields(payload)
    merged_lists = service._merge_axis_lists(
        [{"name": "region"}],
        [{"name": "sales"}],
        payload,
        cast(Any, SimpleNamespace(x_axis_ext=None, y_axis_ext=None, ext_bubble=None, ext_label=None, ext_stack=None, ext_tooltip=None, ext_color=None)),
    )

    assert len(merged) == 9
    assert len(merged_lists) == 9
    assert service._axis_value([{"name": "x"}, "bad"], None) == [{"name": "x"}]
    assert service._result_limit(None) == 1000
    assert service._result_limit(cast(Any, SimpleNamespace(result_count=8))) == 8
    assert service._field_key({"dataeaseName": "sales"}) == "sales"
    assert service._column_reference("*") == "*"
    assert service._column_reference("sales") == 'chart_source."sales"'
    assert service._quote_identifier("schema.table") == '"schema"."table"'
    # Unicode identifiers (e.g. Chinese table names) must be accepted and double-quoted
    assert service._quote_identifier("数据1") == '"数据1"'
    assert service._column_reference("数据1") == 'chart_source."数据1"'
    with pytest.raises(ValueError):
        service._quote_identifier("bad-name")


def test_quote_identifier_unicode_and_sql_safety() -> None:
    r"""Regression: [^\W\d]\w* regex accepts Unicode letters, rejects injection."""
    service = _unit_service()

    assert service._quote_identifier("orders") == '"orders"'
    assert service._quote_identifier("_private") == '"_private"'
    assert service._quote_identifier("table_1") == '"table_1"'
    assert service._quote_identifier("数据1") == '"数据1"'
    assert service._quote_identifier("营业收入") == '"营业收入"'
    assert service._quote_identifier("بيانات") == '"بيانات"'
    assert service._quote_identifier("データ") == '"データ"'
    assert service._quote_identifier("데이터") == '"데이터"'
    assert service._quote_identifier("_数据") == '"_数据"'
    assert service._quote_identifier("public.orders") == '"public"."orders"'
    assert service._quote_identifier("schema.数据1") == '"schema"."数据1"'
    assert service._quote_identifier("  orders  ") == '"orders"'

    for bad in [
        "orders; DROP TABLE users--",
        "1; DROP TABLE users",
        '"); DROP TABLE users--',
        "1table",
        "bad-name",
        "",
        "   ",
        "table name",
        "table@col",
    ]:
        with pytest.raises(ValueError):
            service._quote_identifier(bad)


def test_build_base_sql_and_build_chart_sql_cover_key_paths() -> None:
    service = _unit_service()

    assert service._build_base_sql(" SELECT 1 ", None, []) == "SELECT 1"
    assert service._build_base_sql(None, {"sql": " select * from demo "}, []) == "select * from demo"
    assert service._build_base_sql(None, {"table": "orders"}, []) == 'SELECT * FROM "orders"'
    assert service._build_base_sql(None, {"table": "数据1"}, []) == 'SELECT * FROM "数据1"'
    assert service._build_base_sql(None, None, [SimpleNamespace(table_name="orders")]) == 'SELECT * FROM "orders"'
    assert service._build_base_sql(None, None, []) is None

    sql = service._build_chart_sql(
        "SELECT * FROM orders",
        [{"dataeaseName": "region"}],
        [
            {"dataeaseName": "sales", "summary": "sum"},
            {"dataeaseName": "qty", "summary": "none"},
            {"dataeaseName": "sales", "summary": "count"},
        ],
        50,
    )
    assert 'SUM(chart_source."sales") AS "sales"' in sql
    assert 'chart_source."qty" AS "qty"' in sql
    assert 'COUNT(chart_source."sales") AS "sales"' in sql
    assert 'GROUP BY chart_source."region", chart_source."qty"' in sql
    assert sql.endswith("LIMIT 50")
    assert service._build_chart_sql("SELECT 1", [], [], 5) == "SELECT 1"


@pytest.mark.asyncio
async def test_empty_response_build_external_fields_and_datasource_resolution() -> None:
    service = _unit_service()
    service.sql_executor = cast(Any, SimpleNamespace(_infer_type=lambda rows, index: "numeric" if rows else None))
    empty = service._empty_data_response(
        ChartDataRequest(id=5, scene_id=9, table_id=None, fields=None),
        None,
        [{"name": "region"}],
    )
    fields = service._build_external_fields(
        [FakeRecord(region="east", sales=Decimal("1.5"))],
        [["east", Decimal("1.5")]],
    )

    class FakeDatasourceRepo:
        async def get_by_id(self, datasource_id: int) -> object:
            return SimpleNamespace(id=datasource_id)

    cast(Any, service).datasource_repo = FakeDatasourceRepo()
    resolved = await service._resolve_datasource(
        [SimpleNamespace(datasource_id=11)],
        None,
    )
    resolved_from_group = await service._resolve_datasource([], SimpleNamespace(info={"datasourceId": "12"}))
    unresolved = await service._resolve_datasource([], SimpleNamespace(info={}))

    assert empty.chart_id == 5
    assert empty.scene_id == 9
    assert fields == [{"name": "region", "type": "numeric"}, {"name": "sales", "type": "numeric"}]
    assert cast(Any, resolved).id == 11
    assert cast(Any, resolved_from_group).id == 12
    assert unresolved is None


@pytest.mark.asyncio
async def test_execute_chart_sql_uses_sql_executor_without_datasource() -> None:
    service = _unit_service()

    async def _resolve(*_args: object, **_kwargs: object) -> None:
        return None

    async def _execute(sql: str, limit: int = 1000) -> dict[str, object]:
        return {"sql": sql, "data": [[1]], "fields": [{"name": "a", "type": "integer"}], "total": 1, "limit": limit}

    cast(Any, service)._resolve_datasource = _resolve
    service.sql_executor = cast(Any, SimpleNamespace(execute_select=_execute))

    payload = await service._execute_chart_sql("SELECT 1", [], None)
    assert payload["sql"] == "SELECT 1"
    assert payload["total"] == 1


@pytest.mark.asyncio
async def test_execute_chart_sql_uses_external_datasource_connection() -> None:
    service = _unit_service()
    records = [FakeRecord(region="east", sales=Decimal("8.5"))]
    connection = FakeConnection(records)

    async def _resolve(*_args: object, **_kwargs: object) -> object:
        return SimpleNamespace(configuration={"host": "x"}, type="MySQL")

    cast(Any, service)._resolve_datasource = _resolve

    class FakeDatasourceService:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        async def _open_connection(self, _config: dict[str, object]) -> FakeConnection:
            return connection

        @staticmethod
        def _is_file_type(datasource_type: str) -> bool:
            return datasource_type in {"Excel", "ExcelRemote"}

    from app import services as _services_pkg  # pyright: ignore[reportImplicitRelativeImport]
    from app.services import chart_service as chart_service_module  # pyright: ignore[reportImplicitRelativeImport]

    _ = _services_pkg
    original = chart_service_module.DatasourceService
    chart_service_module.DatasourceService = FakeDatasourceService  # type: ignore[assignment]
    try:
        payload = await service._execute_chart_sql("SELECT * FROM ext", [SimpleNamespace()], SimpleNamespace())
    finally:
        chart_service_module.DatasourceService = original  # type: ignore[assignment]

    assert payload["data"] == [["east", Decimal("8.5")]]
    assert payload["fields"] == [{"name": "region", "type": "varchar"}, {"name": "sales", "type": "numeric"}]
    assert connection.sql == "SELECT * FROM ext"
    assert connection.closed is True


async def test_execute_chart_sql_file_type_datasource_uses_internal_executor() -> None:
    service = _unit_service()

    async def _resolve(*_args: object, **_kwargs: object) -> object:
        return SimpleNamespace(configuration=[{"file": "data.xlsx"}], type="Excel")

    cast(Any, service)._resolve_datasource = _resolve

    internal_result: dict[str, object] = {"sql": "ok", "data": [["a"]], "fields": [], "total": 1}

    class FakeSQLExecutor:
        async def execute_select(self, sql: str, limit: int = 1000) -> dict[str, object]:
            return internal_result

    cast(Any, service).sql_executor = FakeSQLExecutor()

    from app.services import chart_service as chart_service_module  # pyright: ignore[reportImplicitRelativeImport]

    original = chart_service_module.DatasourceService

    class ShouldNotBeCalledService:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        async def _open_connection(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("Should not open external connection for file-type datasource")

        @staticmethod
        def _is_file_type(datasource_type: str) -> bool:
            return datasource_type in {"Excel", "ExcelRemote"}

    chart_service_module.DatasourceService = ShouldNotBeCalledService  # type: ignore[assignment]
    try:
        result = await service._execute_chart_sql("SELECT * FROM \"数据1\"", [SimpleNamespace()], SimpleNamespace())
    finally:
        chart_service_module.DatasourceService = original  # type: ignore[reportImplicitRelativeImport]

    assert result is internal_result


class TestChartServiceIntegration:
    pytestmark = [
        pytest.mark.asyncio,
        pytest.mark.skipif(
            os.getenv("DE_E2E") != "1",
            reason="Requires PostgreSQL (set DE_E2E=1)",
        ),
    ]

    async def test_save_get_update_view_list_detail_and_delete(self, db_session: AsyncSession) -> None:
        service = _service(db_session)
        viz_repo = DatasetGroupRepository(db_session)
        _ = viz_repo
        chart_ids: list[int] = []
        field_ids: list[int] = []
        table_ids: list[int] = []
        group_ids: list[int] = []
        datasource_ids: list[int] = []
        visualization_ids: list[int] = []
        try:
            scene = DataVisualizationInfo(**_viz_payload(_stamp()))
            db_session.add(scene)
            await db_session.commit()
            visualization_ids.append(scene.id)

            dataset = await DatasetGroupRepository(db_session).create(_group_payload(_stamp()))
            table = await DatasetTableRepository(db_session).create(
                _table_payload(_stamp(), group_id=dataset.id, table_name="orders")
            )
            field = await DatasetFieldRepository(db_session).create(
                _field_payload(group_id=dataset.id, table_id=table.id, origin_name="region", name="Region", index=0)
            )
            group_ids.append(dataset.id)
            table_ids.append(table.id)
            field_ids.append(field.id)

            created = await service.save(
                ChartSaveRequest(
                    title="sales",
                    scene_id=scene.id,
                    table_id=table.id,
                    type="bar",
                    render="antv",
                    x_axis=[{"name": "region", "dataeaseName": "region"}],
                    y_axis=[{"name": "sales", "dataeaseName": "sales", "summary": "sum"}],
                ),
                _user(),
            )
            chart_ids.append(created.id)

            fetched = await service.get_by_id(created.id)
            details = await service.get_detail(created.id)
            listed = await service.view_detail_list(scene.id)
            updated = await service.update(
                ChartUpdateRequest(
                    id=created.id,
                    title="sales-updated",
                    scene_id=scene.id,
                    table_id=table.id,
                    type="line",
                    render="antv",
                ),
                _user(),
            )

            assert fetched.id == created.id
            assert details.chart.id == created.id
            assert details.fields[0].origin_name == "region"
            assert listed[0].id == created.id
            assert updated.title == "sales-updated"
            assert updated.type == "line"

            await service.delete(created.id)
            chart_ids.clear()
            with pytest.raises(HTTPException):
                await service.get_by_id(created.id)
        finally:
            await _cleanup_entities(
                db_session,
                chart_ids=chart_ids,
                field_ids=field_ids,
                table_ids=table_ids,
                group_ids=group_ids,
                datasource_ids=datasource_ids,
                visualization_ids=visualization_ids,
            )

    async def test_get_data_success_missing_group_and_exception_fallbacks(self, db_session: AsyncSession) -> None:
        service = _service(db_session)
        chart_ids: list[int] = []
        field_ids: list[int] = []
        table_ids: list[int] = []
        group_ids: list[int] = []
        datasource_ids: list[int] = []
        visualization_ids: list[int] = []
        try:
            scene = DataVisualizationInfo(**_viz_payload(_stamp(), name="data-scene"))
            db_session.add(scene)
            await db_session.commit()
            visualization_ids.append(scene.id)

            dataset = await DatasetGroupRepository(db_session).create(
                _group_payload(_stamp(), union_sql="SELECT 'east' AS region, 8 AS sales")
            )
            table = await DatasetTableRepository(db_session).create(
                _table_payload(_stamp(), group_id=dataset.id, table_name="orders")
            )
            group_ids.append(dataset.id)
            table_ids.append(table.id)

            chart = await ChartRepository(db_session).create(_chart_payload(_stamp(), scene_id=scene.id, table_id=dataset.id))
            chart_ids.append(chart.id)

            payload = await service.get_data(ChartDataRequest(id=chart.id, table_id=dataset.id, fields=None))
            missing_group = await service.get_data(ChartDataRequest(id=chart.id, table_id=_stamp(), fields=None))
            no_table = await service.get_data(ChartDataRequest(id=None, table_id=None, fields=None))

            assert payload.total == 1
            assert cast(Any, payload.data[0])["value"] == 8
            assert payload.chart_id == chart.id
            assert missing_group.total == 0
            assert no_table.total == 0
            assert no_table.chart_id is None

            original = service._execute_chart_sql

            async def _boom(*_args: object, **_kwargs: object) -> dict[str, object]:
                raise RuntimeError("boom")

            service._execute_chart_sql = _boom  # type: ignore[method-assign]
            try:
                fallback = await service.get_data(ChartDataRequest(id=chart.id, table_id=dataset.id, fields=None))
            finally:
                service._execute_chart_sql = original  # type: ignore[assignment]

            assert fallback.total == 0
            assert fallback.chart_id == chart.id
        finally:
            await _cleanup_entities(
                db_session,
                chart_ids=chart_ids,
                field_ids=field_ids,
                table_ids=table_ids,
                group_ids=group_ids,
                datasource_ids=datasource_ids,
                visualization_ids=visualization_ids,
            )

    async def test_get_data_uses_external_datasource_and_view_fields(self, db_session: AsyncSession) -> None:
        service = _service(db_session)
        chart_ids: list[int] = []
        field_ids: list[int] = []
        table_ids: list[int] = []
        group_ids: list[int] = []
        datasource_ids: list[int] = []
        visualization_ids: list[int] = []
        try:
            scene = DataVisualizationInfo(**_viz_payload(_stamp(), name="external-scene"))
            db_session.add(scene)
            await db_session.commit()
            visualization_ids.append(scene.id)

            datasource = await DatasourceRepository(db_session).create(_datasource_payload(_stamp()))
            dataset = await DatasetGroupRepository(db_session).create(_group_payload(_stamp(), info={"datasourceId": datasource.id}))
            table = await DatasetTableRepository(db_session).create(
                _table_payload(_stamp(), group_id=dataset.id, datasource_id=datasource.id, table_name="orders")
            )
            datasource_ids.append(datasource.id)
            group_ids.append(dataset.id)
            table_ids.append(table.id)

            chart = await ChartRepository(db_session).create(_chart_payload(_stamp(), scene_id=scene.id, table_id=dataset.id))
            chart_ids.append(chart.id)

            records = [FakeRecord(region="north", sales=Decimal("3.2"))]
            connection = FakeConnection(records)

            class FakeDatasourceService:
                def __init__(self, *_args: object, **_kwargs: object) -> None:
                    pass

                async def _open_connection(self, _config: dict[str, object]) -> FakeConnection:
                    return connection

                @staticmethod
                def _is_file_type(datasource_type: str) -> bool:
                    return datasource_type in {"Excel", "ExcelRemote"}

            from app.services import chart_service as chart_service_module  # pyright: ignore[reportImplicitRelativeImport]

            original = chart_service_module.DatasourceService
            chart_service_module.DatasourceService = FakeDatasourceService  # type: ignore[assignment]
            try:
                payload = await service.get_data(
                    ChartDataRequest(
                        id=chart.id,
                        table_id=dataset.id,
                        view_fields=[{"name": "provided"}],
                        fields=None,
                    )
                )
            finally:
                chart_service_module.DatasourceService = original  # type: ignore[assignment]

            assert payload.fields == [{"name": "provided"}]
            assert payload.total == 1
            assert connection.closed is True
        finally:
            await _cleanup_entities(
                db_session,
                chart_ids=chart_ids,
                field_ids=field_ids,
                table_ids=table_ids,
                group_ids=group_ids,
                datasource_ids=datasource_ids,
                visualization_ids=visualization_ids,
            )

    async def test_missing_chart_raises_not_found(self, db_session: AsyncSession) -> None:
        service = _service(db_session)

        with pytest.raises(HTTPException) as get_exc:
            await service.get_by_id(_stamp())
        with pytest.raises(HTTPException) as update_exc:
            await service.update(
                ChartUpdateRequest(
                    id=_stamp(),
                    title="x",
                    scene_id=_stamp(),
                    table_id=None,
                    type="bar",
                    render="antv",
                ),
                _user(),
            )

        assert get_exc.value.status_code == 404
        assert update_exc.value.status_code == 404
