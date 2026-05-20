from __future__ import annotations

import logging
import re
import time
from collections.abc import Sequence
from typing import Any, cast
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.chart import CoreChartView
from app.models.dataset import CoreDatasetTableField
from app.models.datasource import CoreDatasource
from app.repositories.chart_repo import ChartRepository
from app.repositories.dataset_repo import DatasetFieldRepository, DatasetGroupRepository, DatasetTableRepository
from app.repositories.datasource_repo import DatasourceRepository
from app.schemas.auth import TokenUser
from app.schemas.chart import (
    ChartDataRequest,
    ChartDataResponse,
    ChartDetailResponse,
    ChartDrillRequest,
    ChartFieldEnumRequest,
    ChartFieldResponse,
    ChartResponse,
    ChartSaveRequest,
    ChartUpdateRequest,
    DatasetExportRequest,
)
from app.services.chart_data_builder import ChartDataBuilder
from app.services.dataset_service import DatasetService
from app.services.datasource_service import DatasourceService, _as_config_dict
from app.services.sql_executor import SQLExecutor

logger = logging.getLogger(__name__)

_SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SUMMARY_TO_AGGREGATE = {
    "sum": "SUM",
    "avg": "AVG",
    "average": "AVG",
    "count": "COUNT",
    "max": "MAX",
    "min": "MIN",
    "stddev": "STDDEV",
    "variance": "VARIANCE",
}


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


@final
class ChartService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chart_repo = ChartRepository(session)
        self.field_repo = DatasetFieldRepository(session)
        self.group_repo = DatasetGroupRepository(session)
        self.table_repo = DatasetTableRepository(session)
        self.datasource_repo = DatasourceRepository(session)
        self.sql_executor = SQLExecutor()

    async def get_by_id(self, chart_id: int) -> ChartResponse:
        chart = await self._get_chart(chart_id)
        return ChartResponse.model_validate(chart)

    async def save(self, payload: ChartSaveRequest, user: TokenUser) -> ChartResponse:
        now = _timestamp_ms()
        created = await self.chart_repo.create({
            **payload.model_dump(by_alias=False, exclude_none=True),
            "id": payload.id or _new_identifier(),
            "create_by": str(user.user_id),
            "create_time": now,
            "update_time": now,
        })
        return ChartResponse.model_validate(created)

    async def update(self, payload: ChartUpdateRequest, user: TokenUser) -> ChartResponse:
        existing = await self._get_chart(payload.id)
        update_data = payload.model_dump(by_alias=False, exclude_none=True)
        update_data["update_time"] = _timestamp_ms()
        update_data.setdefault("create_by", existing.create_by)
        _ = user
        updated = await self.chart_repo.update(existing, update_data)
        return ChartResponse.model_validate(updated)

    async def delete(self, chart_id: int) -> None:
        chart = await self._get_chart(chart_id)
        await self.chart_repo.delete(chart)

    async def get_data(self, payload: ChartDataRequest) -> ChartDataResponse:
        chart = await self._get_optional_chart(payload.id)
        x_axis = self._axis_value(payload.x_axis, chart.x_axis if chart else None)
        y_axis = self._axis_value(payload.y_axis, chart.y_axis if chart else None)
        fields_source = payload.view_fields if payload.view_fields is not None else (chart.view_fields if chart else None)
        if fields_source is None:
            fields_source = self._merge_axis_lists(x_axis, y_axis, payload, chart)
        normalized_fields = list(fields_source) if isinstance(fields_source, list) else []
        response = self._empty_data_response(payload, chart, normalized_fields)

        table_id = payload.table_id or (chart.table_id if chart else None)
        if table_id is None:
            return response

        try:
            dataset_group = await self.group_repo.get_by_id(table_id)
            if dataset_group is None:
                return response

            dataset_tables = list(await self.table_repo.list_by_group(dataset_group.id))
            base_sql = self._build_base_sql(dataset_group.union_sql, dataset_group.info, dataset_tables)
            if base_sql is None:
                return response

            limit = self._result_limit(chart)
            chart_sql = self._build_chart_sql(base_sql, x_axis, y_axis, limit)
            query_result = await self._execute_chart_sql(chart_sql, dataset_tables, dataset_group)
            result_fields = cast(list[dict[str, Any]], query_result.get("fields", []))
            rows = cast(list[list[Any]], query_result.get("data", []))
            chart_type = str(chart.chart_type or chart.type or "") if chart else ""
            chart_data = ChartDataBuilder.build_antv_data(rows, result_fields, x_axis, y_axis, chart_type)
            return ChartDataResponse(
                fields=cast(list[object], normalized_fields if normalized_fields else cast(list[object], result_fields)),
                data=cast(list[object], chart_data),
                total=len(chart_data),
                chart_id=response.chart_id,
                scene_id=response.scene_id,
            )
        except Exception as exc:
            logger.exception("chart get_data execution failed", extra={"chart_id": payload.id, "table_id": table_id})
            response_fields = list(response.fields) if response.fields else []
            return ChartDataResponse(
                fields=response_fields,
                data=[],
                total=0,
                chart_id=response.chart_id,
                scene_id=response.scene_id,
                error=str(exc),
            )

    async def get_detail(self, chart_id: int) -> ChartDetailResponse:
        chart = await self._get_chart(chart_id)
        fields = []
        if chart.table_id is not None:
            fields = [ChartFieldResponse.model_validate(item) for item in await self.field_repo.list_by_table(chart.table_id)]
        return ChartDetailResponse(chart=ChartResponse.model_validate(chart), fields=fields)

    async def view_detail_list(self, scene_id: int) -> list[ChartResponse]:
        charts = await self.chart_repo.list_by_scene(scene_id)
        return [ChartResponse.model_validate(chart) for chart in charts]

    async def inner_export_dataset_details(self, payload: DatasetExportRequest | dict[str, object]) -> dict[str, object]:
        request_payload = payload.model_dump(by_alias=False) if isinstance(payload, DatasetExportRequest) else payload
        chart_id = request_payload.get("chartId") or request_payload.get("chart_id")
        dataset_group_id = request_payload.get("datasetGroupId") or request_payload.get("dataset_group_id")

        if chart_id is not None:
            chart = await self._get_optional_chart(int(str(chart_id)))
            if chart is not None and chart.table_id is not None:
                dataset_group_id = chart.table_id

        if dataset_group_id is None:
            return {"fields": [], "data": [], "total": 0}

        group_id = int(str(dataset_group_id))
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            return {"fields": [], "data": [], "total": 0}

        dataset_tables = list(await self.table_repo.list_by_group(group_id))
        base_sql = DatasetService._build_dataset_sql_static(group)
        if base_sql is None:
            base_sql = self._build_base_sql(group.union_sql, group.info, dataset_tables)
        if base_sql is None:
            return {"fields": [], "data": [], "total": 0}

        result = await self._execute_chart_sql(base_sql, dataset_tables, group, limit=100000)
        if result.get("fields"):
            return result
        fields = await self.field_repo.list_checked_by_group_no_chart_filter(group_id)
        return {
            **result,
            "fields": [DatasetService._field_to_dict(field) for field in fields],
        }

    async def list_fields_by_dq(self, dataset_group_id: int, chart_id: int) -> list[dict[str, object]]:
        await self.group_repo.get_by_id(dataset_group_id)
        fields = await self.field_repo.list_by_chart(dataset_group_id, chart_id)
        return [DatasetService._field_to_dict(field) for field in fields]

    async def copy_field(self, field_id: int, chart_id: int) -> dict[str, object]:
        chart = await self._get_optional_chart(chart_id)
        if chart is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
        source = await self.session.get(CoreDatasetTableField, field_id)
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
        copied = await self.field_repo.copy_field_to_chart(field_id, chart_id)
        return DatasetService._field_to_dict(copied)

    async def delete_chart_field(self, field_id: int) -> None:
        field = await self.session.get(CoreDatasetTableField, field_id)
        if field is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
        if field.chart_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Field is not a chart custom field")
        await self.field_repo.delete_chart_field(field_id)

    async def delete_all_chart_fields(self, chart_id: int) -> None:
        await self.field_repo.delete_all_chart_fields(chart_id)

    async def get_field_enum_data(
        self, field_id: int, field_type: str, request: ChartFieldEnumRequest
    ) -> list[dict[str, object]]:
        _ = field_type
        field = await self.session.get(CoreDatasetTableField, field_id)
        if field is None or field.dataset_group_id is None:
            return []
        column_name = field.dataease_name or field.origin_name
        if not isinstance(column_name, str) or not column_name.strip():
            return []

        group = await self.group_repo.get_by_id(field.dataset_group_id)
        if group is None:
            return []
        base_sql = DatasetService._build_dataset_sql_static(group)
        if not base_sql:
            return []

        sql = (
            f'SELECT DISTINCT {self._quote_identifier(column_name.strip())} '
            f'FROM ({base_sql}) AS chart_enum LIMIT {max(1, request.result_limit)}'
        )
        tables = list(await self.table_repo.list_by_group(field.dataset_group_id))
        result = await self._execute_chart_sql(sql, tables, group)
        rows = cast(list[list[Any]], result.get("data", []))
        return [
            {"text": "" if not row or row[0] is None else str(row[0]), "value": "" if not row or row[0] is None else str(row[0])}
            for row in rows
        ]

    async def get_drill_field_data(self, field_id: int, request: ChartDrillRequest) -> list[dict[str, object]]:
        field = await self.session.get(CoreDatasetTableField, field_id)
        if field is None or field.dataset_group_id is None:
            return []
        column_name = field.dataease_name or field.origin_name
        if not isinstance(column_name, str) or not column_name.strip():
            return []

        group = await self.group_repo.get_by_id(field.dataset_group_id)
        if group is None:
            return []
        base_sql = DatasetService._build_dataset_sql_static(group)
        if not base_sql:
            return []

        sql = (
            f'SELECT DISTINCT {self._quote_identifier(column_name.strip())} '
            f'FROM ({base_sql}) AS chart_drill LIMIT 100'
        )
        tables = list(await self.table_repo.list_by_group(field.dataset_group_id))
        result = await self._execute_chart_sql(sql, tables, group)
        rows = cast(list[list[Any]], result.get("data", []))
        _ = request
        return [
            {"text": "" if not row or row[0] is None else str(row[0]), "value": "" if not row or row[0] is None else str(row[0])}
            for row in rows
        ]

    async def check_same_dataset(self, source_view_id: int, target_view_id: int) -> bool:
        source = await self._get_optional_chart(source_view_id)
        target = await self._get_optional_chart(target_view_id)
        if source is None or target is None:
            return False
        return source.table_id == target.table_id

    async def _get_chart(self, chart_id: int) -> CoreChartView:
        chart = await self.chart_repo.get_by_id(chart_id)
        if chart is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
        return chart

    async def _get_optional_chart(self, chart_id: int | None) -> CoreChartView | None:
        if chart_id is None:
            return None
        return await self.chart_repo.get_by_id(chart_id)

    @staticmethod
    def _merge_axis_fields(payload: ChartDataRequest) -> list[object]:
        fields: list[object] = []
        for value in [payload.x_axis, payload.x_axis_ext, payload.y_axis, payload.y_axis_ext, payload.ext_bubble, payload.ext_label, payload.ext_stack, payload.ext_tooltip, payload.ext_color]:
            if isinstance(value, list):
                fields.extend(value)
        return fields

    def _empty_data_response(
        self,
        payload: ChartDataRequest,
        chart: CoreChartView | None,
        fields: list[object],
    ) -> ChartDataResponse:
        return ChartDataResponse(
            fields=fields,
            data=[],
            total=0,
            chart_id=chart.id if chart else payload.id,
            scene_id=chart.scene_id if chart else payload.scene_id,
        )

    def _merge_axis_lists(
        self,
        x_axis: list[dict[str, Any]],
        y_axis: list[dict[str, Any]],
        payload: ChartDataRequest,
        chart: CoreChartView | None,
    ) -> list[object]:
        fields: list[object] = [*x_axis, *y_axis]
        for value in [
            payload.x_axis_ext,
            chart.x_axis_ext if chart else None,
            payload.y_axis_ext,
            chart.y_axis_ext if chart else None,
            payload.ext_bubble,
            chart.ext_bubble if chart else None,
            payload.ext_label,
            chart.ext_label if chart else None,
            payload.ext_stack,
            chart.ext_stack if chart else None,
            payload.ext_tooltip,
            chart.ext_tooltip if chart else None,
            payload.ext_color,
            chart.ext_color if chart else None,
        ]:
            if isinstance(value, list):
                fields.extend(value)
        return fields

    @staticmethod
    def _axis_value(primary: object, fallback: object) -> list[dict[str, Any]]:
        source = primary if primary is not None else fallback
        if not isinstance(source, list):
            return []
        return [item for item in source if isinstance(item, dict)]

    @staticmethod
    def _result_limit(chart: CoreChartView | None) -> int:
        if chart is None or chart.result_count is None or chart.result_count <= 0:
            return 1000
        return chart.result_count

    def _build_base_sql(
        self,
        union_sql: str | None,
        info: object,
        dataset_tables: Sequence[object],
    ) -> str | None:
        if union_sql and union_sql.strip():
            return union_sql.strip()
        if isinstance(info, dict):
            sql = info.get("sql")
            if isinstance(sql, str) and sql.strip():
                return sql.strip()
            table_name = info.get("table") or info.get("tableName") or info.get("table_name")
            if isinstance(table_name, str) and table_name.strip():
                return f'SELECT * FROM {self._quote_identifier(table_name.strip())}'
        first_table = dataset_tables[0] if dataset_tables else None
        table_name = getattr(first_table, "table_name", None)
        if isinstance(table_name, str) and table_name.strip():
            return f'SELECT * FROM {self._quote_identifier(table_name.strip())}'
        return None

    def _build_chart_sql(
        self,
        base_sql: str,
        x_axis: list[dict[str, Any]],
        y_axis: list[dict[str, Any]],
        limit: int,
    ) -> str:
        dimensions = [item for item in x_axis if self._field_key(item)]
        metrics = [item for item in y_axis if self._field_key(item)]

        if not dimensions and not metrics:
            return base_sql

        select_parts: list[str] = []
        group_by_parts: list[str] = []
        for dimension in dimensions:
            column = self._column_reference(self._field_key(dimension))
            alias = self._quote_identifier(self._field_key(dimension))
            select_parts.append(f"{column} AS {alias}")
            group_by_parts.append(column)

        for metric in metrics:
            field_key = self._field_key(metric)
            column = self._column_reference(field_key)
            alias = self._quote_identifier(field_key)
            summary = str(metric.get("summary") or "sum").lower()
            if summary == "none":
                select_parts.append(f"{column} AS {alias}")
                if column not in group_by_parts:
                    group_by_parts.append(column)
                continue
            aggregate = _SUMMARY_TO_AGGREGATE.get(summary, "SUM")
            expression = "COUNT(*)" if aggregate == "COUNT" and field_key in {"*", ""} else f"{aggregate}({column})"
            select_parts.append(f"{expression} AS {alias}")

        sql = f'SELECT {", ".join(select_parts)} FROM ({base_sql}) AS chart_source'
        if group_by_parts and any(str(metric.get("summary") or "sum").lower() != "none" for metric in metrics):
            sql = f'{sql} GROUP BY {", ".join(group_by_parts)}'
        return f"{sql} LIMIT {limit}"

    async def _execute_chart_sql(
        self,
        sql: str,
        dataset_tables: Sequence[object],
        dataset_group: object | None = None,
        limit: int = 1000,
    ) -> dict[str, object]:
        datasource = await self._resolve_datasource(dataset_tables, dataset_group)
        if datasource is None:
            return await self.sql_executor.execute_select(sql, limit=limit)

        datasource_service = DatasourceService(self.session, self.datasource_repo)
        connection = await datasource_service._open_connection(_as_config_dict(datasource.configuration))
        try:
            records = await connection.fetch(sql)
        finally:
            await connection.close()

        rows = [list(record) for record in records]
        fields = self._build_external_fields(records, rows)
        return {"sql": sql, "data": rows, "fields": fields, "total": len(rows)}

    async def _resolve_datasource(self, dataset_tables: Sequence[object], dataset_group: object | None = None) -> CoreDatasource | None:
        first_table = dataset_tables[0] if dataset_tables else None
        datasource_id = getattr(first_table, "datasource_id", None)
        if not isinstance(datasource_id, int) and dataset_group is not None:
            info = getattr(dataset_group, "info", None)
            if isinstance(info, dict):
                raw_id = info.get("datasourceId") or info.get("datasource_id")
                if raw_id is not None:
                    datasource_id = int(str(raw_id))
        if not isinstance(datasource_id, int):
            return None
        return await self.datasource_repo.get_by_id(datasource_id)

    def _build_external_fields(self, records: Sequence[Any], rows: Sequence[list[Any]]) -> list[dict[str, str]]:
        if not records:
            return []
        keys = [str(key) for key in records[0].keys()]
        fields: list[dict[str, str]] = []
        for index, key in enumerate(keys):
            field_type = self.sql_executor._infer_type(rows, index) or "unknown"
            fields.append({"name": key, "type": field_type})
        return fields

    @staticmethod
    def _field_key(field: dict[str, Any]) -> str:
        return str(field.get("dataeaseName") or field.get("dataease_name") or field.get("name") or "")

    def _column_reference(self, identifier: str) -> str:
        if identifier == "*":
            return identifier
        return f'chart_source.{self._quote_identifier(identifier)}'

    def _quote_identifier(self, identifier: str) -> str:
        if "." in identifier:
            return ".".join(self._quote_identifier(part) for part in identifier.split("."))
        cleaned = identifier.strip()
        if not cleaned:
            raise ValueError("SQL identifier must not be empty")
        if not _SAFE_IDENTIFIER_RE.match(cleaned):
            raise ValueError(f"Unsafe SQL identifier: {identifier}")
        return f'"{cleaned}"'


async def get_chart_service(session: AsyncSession = Depends(get_db)) -> ChartService:
    return ChartService(session)
