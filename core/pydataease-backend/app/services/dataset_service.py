from __future__ import annotations

import base64
import json
import re
import time
from collections.abc import Sequence
from importlib import import_module
from typing import Any, cast, final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.dataset import CoreDatasetGroup, CoreDatasetTable, CoreDatasetTableField
from app.models.datasource import CoreDatasource
from app.repositories.dataset_repo import (
    DatasetFieldRepository,
    DatasetGroupRepository,
    DatasetTableRepository,
)
from app.repositories.datasource_repo import DatasourceRepository
from app.services.datasource_drivers import is_supported_type
from app.services.datasource_service import DatasourceService, _as_config_dict
from app.services.sql_executor import apply_limit, validate_readonly_sql
from app.utils.id_utils import _sid
from app.schemas.auth import TokenUser
from app.schemas.dataset import (
    DatasetEnumValueDsRequest,
    DatasetEnumValueRequest,
    DatasetFieldResponse,
    DatasetGroupCreate,
    DatasetGroupMove,
    DatasetGroupRename,
    DatasetGroupUpdate,
    DatasetNodeResponse,
    DatasetPreviewDataRequest,
    DatasetTableFieldRequest,
    DatasetTreeNodeResponse,
)
from app.schemas.datasource import DatasourceFieldResponse

SQLExecutor = import_module("app.services.sql_executor").SQLExecutor

_SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


def _compute_level(all_groups: list[CoreDatasetGroup], pid: int | None) -> int:
    if pid is None or pid == 0:
        return 0
    id_to_level: dict[int, int] = {g.id: g.level or 0 for g in all_groups}
    return (id_to_level.get(pid, 0) or 0) + 1


def _build_tree(groups: list[CoreDatasetGroup]) -> list[DatasetTreeNodeResponse]:
    nodes: dict[int, DatasetTreeNodeResponse] = {}
    for g in groups:
        node = DatasetTreeNodeResponse.model_validate(g)
        node.leaf = g.node_type == "dataset"
        node.children = []
        nodes[g.id] = node

    roots: list[DatasetTreeNodeResponse] = []
    for g in groups:
        node = nodes[g.id]
        if g.pid is None or g.pid == 0 or g.pid not in nodes:
            roots.append(node)
        else:
            nodes[g.pid].children.append(node)
    return roots


@final
class DatasetService:
    session: AsyncSession
    group_repo: DatasetGroupRepository
    table_repo: DatasetTableRepository
    field_repo: DatasetFieldRepository
    sql_executor: Any

    def __init__(
        self,
        session: AsyncSession,
        group_repo: DatasetGroupRepository,
        table_repo: DatasetTableRepository,
        field_repo: DatasetFieldRepository,
    ) -> None:
        self.session = session
        self.group_repo = group_repo
        self.table_repo = table_repo
        self.field_repo = field_repo
        self.sql_executor = SQLExecutor()

    async def tree(self) -> list[dict[str, object]]:
        groups = await self.group_repo.list_all_ordered()
        groups = await self._filter_by_permission(groups)
        built_tree = _build_tree(list(groups))

        def _node_to_dict(node: DatasetTreeNodeResponse) -> dict[str, object]:
            d = node.model_dump(by_alias=True)
            d["id"] = str(d["id"])
            d["pid"] = str(d["pid"]) if d["pid"] is not None else "0"
            d["weight"] = 9
            d["extraFlag"] = 0
            d["extraFlag1"] = 0
            d["children"] = [_node_to_dict(c) for c in (node.children or [])]
            return d

        children: list[dict[str, object]] = [_node_to_dict(n) for n in built_tree]
        root: dict[str, object] = {
            "id": "0",
            "name": "root",
            "pid": -1,
            "leaf": False,
            "weight": 7,
            "extraFlag": 0,
            "extraFlag1": 0,
            "children": children,
        }
        return [root]

    async def create(self, payload: DatasetGroupCreate, user: TokenUser) -> DatasetNodeResponse:
        all_groups = list(await self.group_repo.list_all_ordered())
        pid_value = None if payload.pid == 0 else payload.pid
        level = _compute_level(all_groups, pid_value)

        now = _timestamp_ms()
        info_value = self._normalize_info(payload.info)
        datasource_id, table_name, source_info = self._resolve_source_payload(
            info_value,
            payload.datasource_id,
            payload.table_name,
            payload.union,
        )
        info_value = self._merge_source_info(source_info, datasource_id, table_name)
        info_value = self._attach_union_to_info(info_value, payload.union)

        created = await self.group_repo.create({
            "id": _new_identifier(),
            "name": payload.name.strip(),
            "pid": pid_value,
            "level": level,
            "node_type": payload.node_type,
            "type": payload.type,
            "mode": payload.mode,
            "info": info_value,
            "create_by": str(user.user_id),
            "create_time": now,
            "update_by": str(user.user_id),
            "last_update_time": now,
            "is_cross": payload.is_cross,
        })

        dataset_table = await self._sync_dataset_source(created.id, payload.name.strip(), info_value)

        if payload.all_fields:
            if dataset_table is not None:
                await self.field_repo.delete_by_group(created.id)
            await self._save_fields_for_group(
                created.id,
                self._normalize_fields_for_dataset_table(payload.all_fields, dataset_table),
            )

        return cast(DatasetNodeResponse, cast(object, DatasetNodeResponse.model_validate(created).model_dump(by_alias=True)))

    async def save(self, payload: DatasetGroupUpdate, user: TokenUser) -> DatasetNodeResponse:
        existing = await self._get_group(payload.id)

        all_groups = list(await self.group_repo.list_all_ordered())
        raw_pid = payload.pid if payload.pid is not None else existing.pid
        new_pid = None if raw_pid == 0 else raw_pid
        level = _compute_level(all_groups, new_pid)

        now = _timestamp_ms()
        info_value = payload.info if payload.info is not None else existing.info
        info_value = self._normalize_info(info_value)
        datasource_id, table_name, source_info = self._resolve_source_payload(
            info_value,
            payload.datasource_id,
            payload.table_name,
            payload.union,
        )
        info_value = self._merge_source_info(source_info, datasource_id, table_name)
        info_value = self._attach_union_to_info(info_value, payload.union)

        update_data: dict[str, object] = {
            "update_by": str(user.user_id),
            "last_update_time": now,
            "level": level,
        }
        if payload.name is not None:
            update_data["name"] = payload.name.strip()
        if payload.pid is not None:
            update_data["pid"] = new_pid
        if payload.node_type is not None:
            update_data["node_type"] = payload.node_type
        if payload.type is not None:
            update_data["type"] = payload.type
        if payload.mode is not None:
            update_data["mode"] = payload.mode
        if info_value is not None:
            update_data["info"] = info_value
        if payload.is_cross is not None:
            update_data["is_cross"] = payload.is_cross

        updated = await self.group_repo.update(existing, update_data)
        dataset_table = await self._sync_dataset_source(updated.id, updated.name or "", info_value)

        if payload.all_fields is not None:
            await self.field_repo.delete_by_group(payload.id)
            await self._save_fields_for_group(
                payload.id,
                self._normalize_fields_for_dataset_table(payload.all_fields, dataset_table),
            )

        return cast(DatasetNodeResponse, cast(object, DatasetNodeResponse.model_validate(updated).model_dump(by_alias=True)))

    async def rename(self, payload: DatasetGroupRename, user: TokenUser) -> DatasetNodeResponse:
        existing = await self._get_group(payload.id)
        updated = await self.group_repo.update(existing, {
            "name": payload.name.strip(),
            "update_by": str(user.user_id),
            "last_update_time": _timestamp_ms(),
        })
        return cast(DatasetNodeResponse, cast(object, DatasetNodeResponse.model_validate(updated).model_dump(by_alias=True)))

    async def move(self, payload: DatasetGroupMove, user: TokenUser) -> DatasetNodeResponse:
        existing = await self._get_group(payload.id)
        all_groups = list(await self.group_repo.list_all_ordered())
        pid_value = None if payload.pid == 0 else payload.pid
        level = _compute_level(all_groups, pid_value)
        updated = await self.group_repo.update(existing, {
            "pid": pid_value,
            "level": level,
            "update_by": str(user.user_id),
            "last_update_time": _timestamp_ms(),
        })
        return cast(DatasetNodeResponse, cast(object, DatasetNodeResponse.model_validate(updated).model_dump(by_alias=True)))

    async def delete(self, group_id: int) -> None:
        await self._get_group(group_id)
        await self.group_repo.delete_cascade(group_id)

    async def get_bar_info(self, group_id: int) -> dict[str, object]:
        group = await self._get_group(group_id)
        payload = DatasetNodeResponse.model_validate(group).model_dump(by_alias=True)
        payload["id"] = _sid(payload["id"])
        payload["pid"] = _sid(payload["pid"])
        return payload

    async def get_details(self, group_id: int) -> dict[str, object]:
        group = await self._get_group(group_id)
        fields = await self.field_repo.list_by_group(group_id)
        tables = list(await self.table_repo.list_by_group(group_id))
        payload = DatasetNodeResponse.model_validate(group).model_dump(by_alias=True)
        payload["id"] = _sid(payload["id"])
        payload["pid"] = _sid(payload["pid"])
        payload["allFields"] = [self._field_to_dict(field) for field in fields]
        payload["union"] = self._build_detail_union(group, tables, fields)
        return payload

    async def get_dataset_preview(self, group_id: int) -> dict[str, object]:
        group = await self._get_group(group_id)
        fields = await self.field_repo.list_by_group(group_id)

        file_preview = await self._preview_file_dataset_data(
            group=group,
            dataset_group_id=group_id,
            limit=100,
            offset=0,
        )
        if file_preview is not None:
            raw_total = file_preview.get("total", 0)
            total_value = int(cast(int | str, raw_total)) if isinstance(raw_total, int | str) else 0
            return {
                "id": _sid(group.id),
                "name": group.name,
                "allFields": [self._field_to_dict(field) for field in fields],
                "data": {
                    "fields": file_preview.get("fields", []),
                    "data": file_preview.get("data", []),
                },
                "total": total_value,
            }

        base_sql = await self._build_dataset_sql(group)
        data_result: dict[str, object]
        total = 0
        if base_sql:
            preview_sql = f"SELECT * FROM ({base_sql}) AS dataset_preview LIMIT 100"
            data_result = await self._execute_dataset_sql(preview_sql, group_id)
            count_sql = f"SELECT COUNT(*) AS cnt FROM ({base_sql}) AS dataset_count"
            count_result = await self._execute_dataset_sql(count_sql, group_id)
            rows = cast(list[list[object]], count_result.get("data", []))
            total = int(cast(int | str, rows[0][0])) if rows else 0
        else:
            data_result = {"fields": [], "data": []}

        return {
            "id": _sid(group.id),
            "name": group.name,
            "allFields": [self._field_to_dict(field) for field in fields],
            "data": data_result,
            "total": total,
        }

    async def get_dataset_total(self, group_id: int) -> int:
        group = await self._get_group(group_id)
        file_preview = await self._preview_file_dataset_data(
            group=group,
            dataset_group_id=group_id,
            limit=1,
            offset=0,
        )
        if file_preview is not None:
            raw_total = file_preview.get("total", 0)
            return int(cast(int | str, raw_total)) if isinstance(raw_total, int | str) else 0

        base_sql = await self._build_dataset_sql(group)
        if base_sql is None:
            return 0
        count_sql = f"SELECT COUNT(*) AS cnt FROM ({base_sql}) AS dataset_count"
        result = await self._execute_dataset_sql(count_sql, group_id)
        rows = cast(list[list[object]], result.get("data", []))
        return int(cast(int | str, rows[0][0])) if rows else 0

    async def preview_data(self, request: DatasetPreviewDataRequest) -> dict[str, object]:
        limit = max(1, request.limit)
        offset = max(0, request.offset)

        if request.dataset_group_id:
            group = await self._get_group(request.dataset_group_id)
            fields = await self.field_repo.list_checked_by_group_no_chart_filter(request.dataset_group_id)
            if not fields:
                return {"allFields": [], "data": {"fields": [], "data": [], "total": 0}}

            file_preview = await self._preview_file_dataset_data(
                group=group,
                dataset_group_id=request.dataset_group_id,
                limit=limit,
                offset=offset,
            )
            if file_preview is not None:
                return {
                    "allFields": [self._field_to_dict(field) for field in fields],
                    "data": file_preview,
                }

            base_sql = await self._build_dataset_sql(group)
            if base_sql is None:
                return {"allFields": [], "data": {"fields": [], "data": [], "total": 0}}

            sql = f"SELECT * FROM ({base_sql}) AS dataset_preview LIMIT {limit} OFFSET {offset}"
            result = await self._execute_dataset_sql(sql, request.dataset_group_id)
            return {
                "allFields": [self._field_to_dict(field) for field in fields],
                "data": result,
            }

        if request.union:
            file_preview = await self._preview_file_union_data(
                union_data=request.union,
                limit=limit,
                offset=offset,
            )
            if file_preview is not None:
                return {
                    "allFields": self._normalize_preview_all_fields(request.all_fields),
                    "data": file_preview,
                }

            base_sql = self._build_sql_from_union(request.union)
            datasource_id = self._extract_union_datasource_id(request.union)
            if base_sql is None or datasource_id is None:
                return {"allFields": self._normalize_preview_all_fields(request.all_fields), "data": {"fields": [], "data": [], "total": 0}}

            sql = f"SELECT * FROM ({base_sql}) AS dataset_preview LIMIT {limit} OFFSET {offset}"
            result = await self._execute_sql_for_datasource(sql, datasource_id)
            return {
                "allFields": self._normalize_preview_all_fields(request.all_fields),
                "data": result,
            }

        return {"allFields": [], "data": {"fields": [], "data": [], "total": 0}}

    async def get_enum_values(self, request: DatasetEnumValueRequest) -> list[str]:
        group = await self._get_group(request.dataset_group_id)
        if request.field_id is None:
            return []

        file_preview = await self._preview_file_dataset_data(
            group=group,
            dataset_group_id=request.dataset_group_id,
            limit=max(1, request.result_limit),
            offset=0,
        )
        if file_preview is not None:
            fields = await self.field_repo.list_by_group(request.dataset_group_id)
            target = next((field for field in fields if field.id == request.field_id), None)
            if target is None:
                return []

            column_name = target.dataease_name or target.origin_name
            if not isinstance(column_name, str) or not column_name.strip():
                return []

            rows = cast(list[object], file_preview.get("data", []))
            values: list[str] = []
            seen: set[str] = set()
            for row in rows:
                if not isinstance(row, dict):
                    continue
                raw_value = row.get(column_name)
                normalized = "" if raw_value is None else str(raw_value)
                if normalized in seen:
                    continue
                seen.add(normalized)
                values.append(normalized)
                if len(values) >= max(1, request.result_limit):
                    break
            return values

        base_sql = await self._build_dataset_sql(group)
        if base_sql is None:
            return []

        fields = await self.field_repo.list_by_group(request.dataset_group_id)
        target = next((field for field in fields if field.id == request.field_id), None)
        if target is None:
            return []

        column_name = target.dataease_name or target.origin_name
        if not isinstance(column_name, str) or not column_name.strip():
            return []

        sql = (
            f'SELECT DISTINCT {self._quote_identifier(column_name.strip())} '
            f'FROM ({base_sql}) AS dataset_enum LIMIT {max(1, request.result_limit)}'
        )
        result = await self._execute_dataset_sql(sql, request.dataset_group_id)
        rows = cast(list[list[object]], result.get("data", []))
        return ["" if not row or row[0] is None else str(row[0]) for row in rows]

    async def get_enum_value_objects(self, request: DatasetEnumValueRequest) -> list[dict[str, str]]:
        values = await self.get_enum_values(request)
        return [{"text": value, "value": value} for value in values]

    async def get_enum_values_from_datasource(self, request: DatasetEnumValueDsRequest) -> list[str]:
        datasource_id, table_name, column_name = self._resolve_enum_ds_params(request)

        if datasource_id is None or not table_name or not column_name:
            return []

        datasource = await DatasourceRepository(self.session).get_by_id(datasource_id)
        if datasource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")

        limit = max(1, request.result_limit)

        # For file-type datasources, use the union-based preview which
        # correctly re-parses the stored Excel/CSV content.
        if DatasourceService._is_file_type(datasource.type):
            union_data = None
            dataset_payload = request.dataset
            if isinstance(dataset_payload, dict):
                union_data = dataset_payload.get("union")
            if isinstance(union_data, list) and union_data:
                return await self._enum_values_from_file_union(
                    union_data, column_name, limit,
                )
            # Fallback: no union data, try datasource preview
            return await self._enum_values_from_file_datasource(
                datasource, table_name, column_name, limit,
            )

        sql = (
            f'SELECT DISTINCT {self._quote_identifier(column_name)} '
            f'FROM {self._quote_identifier(table_name)} LIMIT {limit}'
        )
        ds_service = DatasourceService(self.session, DatasourceRepository(self.session))
        config = datasource.configuration
        if isinstance(config, str):
            config = json.loads(config)
        connection = await ds_service._open_connection(_as_config_dict(config), ds_type=datasource.type)
        try:
            records = await connection.fetch(sql)
        finally:
            await connection.close()
        return ["" if record[0] is None else str(record[0]) for record in records]

    @staticmethod
    def _resolve_enum_ds_params(
        request: DatasetEnumValueDsRequest,
    ) -> tuple[int | None, str | None, str | None]:
        if request.datasource_id is not None and request.table_name and request.column_name:
            return request.datasource_id, request.table_name.strip(), request.column_name.strip()

        dataset_payload = request.dataset
        if isinstance(dataset_payload, dict):
            union_data = dataset_payload.get("union")
            if isinstance(union_data, list) and union_data:
                ds_id, tbl_name_raw, _ = DatasetService._extract_source_from_union(union_data)
                tbl_name = tbl_name_raw if isinstance(tbl_name_raw, str) and tbl_name_raw.strip() else None
                col_name: str | None = None
                field_payload = request.field
                if isinstance(field_payload, dict):
                    raw_col = (
                        field_payload.get("dataeaseName")
                        or field_payload.get("originName")
                        or field_payload.get("name")
                    )
                    col_name = raw_col.strip() if isinstance(raw_col, str) and raw_col.strip() else None
                return ds_id, tbl_name, col_name

        return None, None, None

    async def _enum_values_from_file_datasource(
        self,
        datasource: CoreDatasource,
        table_name: str,
        column_name: str,
        limit: int,
    ) -> list[str]:
        ds_service = DatasourceService(self.session, DatasourceRepository(self.session))
        preview = await ds_service.preview_data(
            {"datasourceId": datasource.id, "tableName": table_name},
        )
        # DatasourceService.preview_data returns {"data": {"fields": [...], "data": [...]}}
        outer = preview.get("data")
        if isinstance(outer, dict):
            data_rows = outer.get("data")
        elif isinstance(outer, list):
            data_rows = outer
        else:
            return []
        if not isinstance(data_rows, list):
            return []

        return self._extract_distinct_values(data_rows, column_name, limit)

    async def _enum_values_from_file_union(
        self,
        union_data: list[object],
        column_name: str,
        limit: int,
    ) -> list[str]:
        """Extract distinct enum values from file-type dataset via union preview."""
        file_preview = await self._preview_file_union_data(
            union_data=union_data,
            limit=1000,
            offset=0,
        )
        if file_preview is None:
            return []
        data_rows = file_preview.get("data")
        if not isinstance(data_rows, list):
            return []
        return self._extract_distinct_values(data_rows, column_name, limit)

    @staticmethod
    def _extract_distinct_values(
        data_rows: list[object],
        column_name: str,
        limit: int,
    ) -> list[str]:
        values: list[str] = []
        seen: set[str] = set()
        for row in data_rows:
            if not isinstance(row, dict):
                continue
            raw = row.get(column_name)
            normalized = "" if raw is None else str(raw)
            if normalized not in seen:
                seen.add(normalized)
                values.append(normalized)
                if len(values) >= limit:
                    break
        return values

    async def get_field_tree(self, dataset_group_id: int) -> dict[str, object]:
        fields = await self.field_repo.list_checked_by_group_no_chart_filter(dataset_group_id)
        dimensions = [self._field_to_dict(field) for field in fields if field.group_type == "d"]
        quotas = [self._field_to_dict(field) for field in fields if field.group_type == "q"]
        return {
            "dimensionList": dimensions,
            "quotaList": quotas,
        }

    async def ds_details(self, payload: object) -> list[dict[str, object]]:
        """Return dataset details for a list of table IDs."""
        raw_ids = payload if isinstance(payload, list) else payload.get("ids", []) if isinstance(payload, dict) else []
        ids: list[object] = raw_ids if isinstance(raw_ids, list) else []
        if not ids:
            return []

        results: list[dict[str, object]] = []
        for table_id in ids:
            try:
                table_id_int = int(str(table_id))
                table = await self.table_repo.get_by_id(table_id_int)
                if table is None:
                    continue
                fields = await self.field_repo.list_by_table(table_id_int)
                results.append({
                    "id": _sid(table.id),
                    "name": table.name or "",
                    "dataSourceId": _sid(table.datasource_id),
                    "datasetGroupId": _sid(table.dataset_group_id),
                    "type": table.type,
                    "fields": [
                        {
                            "id": _sid(f.id),
                            "originName": f.origin_name,
                            "name": f.name,
                            "dataeaseName": f.dataease_name,
                            "type": f.type,
                            "deType": f.de_type,
                            "groupType": f.group_type,
                            "checked": f.checked,
                        }
                        for f in fields
                    ],
                })
            except (ValueError, TypeError, AttributeError):
                continue
        return results

    async def get_fields(self, request: DatasetTableFieldRequest) -> list[dict[str, object]]:
        if request.dataset_group_id:
            fields = await self.field_repo.list_by_group(request.dataset_group_id)
            return [DatasetFieldResponse.model_validate(field).model_dump(by_alias=True) for field in fields]

        if request.datasource_id and request.table_name:
            fields = await self._load_datasource_fields(request.datasource_id, request.table_name)
            return [
                self._datasource_field_to_response_dict(field, request.datasource_id, idx)
                for idx, field in enumerate(fields)
            ]

        return []

    async def preview_sql(self, payload: dict[str, object]) -> dict[str, object]:
        raw_sql = str(payload.get("sql", ""))
        try:
            sql = base64.b64decode(raw_sql).decode("utf-8") if raw_sql else ""
        except Exception:
            sql = raw_sql

        datasource_id = payload.get("datasourceId") or payload.get("datasource_id")

        if datasource_id:
            datasource_id_int = int(str(datasource_id))
            ds_repo = DatasourceRepository(self.session)
            datasource = await ds_repo.get_by_id(datasource_id_int)
            if datasource is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")
            if not is_supported_type(datasource.type):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Datasource type '{datasource.type}' does not support SQL preview",
                )
            config = datasource.configuration
            if isinstance(config, str):
                config = json.loads(config)
            if not isinstance(config, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Datasource configuration must be an object",
                )
            sql = validate_readonly_sql(sql)
            sql_with_limit = apply_limit(sql)
            ds_service = DatasourceService(self.session, ds_repo)
            connection = await ds_service._open_connection(config, ds_type=datasource.type)
            try:
                records = await connection.fetch(sql_with_limit)
            finally:
                await connection.close()
            rows = [list(record) for record in records]
            fields = self._build_external_fields(records, rows)
            return {"sql": sql_with_limit, "data": rows, "fields": fields, "total": len(rows)}

        # BUG-044 fix: Do NOT execute arbitrary SQL against internal metadata DB
        # A datasourceId is required for SQL preview execution
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="datasourceId is required for SQL preview",
        )

    def _build_external_fields(self, records: Sequence[Any], rows: Sequence[list[Any]]) -> list[dict[str, str]]:
        if not records:
            return []
        keys = [str(key) for key in records[0].keys()]
        fields: list[dict[str, str]] = []
        for index, key in enumerate(keys):
            field_type = self.sql_executor._infer_type(rows, index) or "unknown"
            fields.append({"name": key, "type": field_type})
        return fields

    async def export_dataset(self, payload: dict[str, object]) -> dict[str, object]:
        rows = payload.get("data") if isinstance(payload, dict) else None
        return {
            "rows": rows if isinstance(rows, list) else [],
            "msg": "Dataset export payload accepted",
        }

    async def per_delete(self, group_id: int) -> bool:
        group = await self.group_repo.get_by_id(group_id)
        return group is not None

    async def _get_group(self, group_id: int) -> CoreDatasetGroup:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        return group

    async def _save_fields_for_group(self, group_id: int, fields_data: Sequence[object]) -> None:
        existing_fields = {
            self._field_identity(field): field
            for field in await self.field_repo.list_by_group(group_id)
            if self._field_identity(field) is not None
        }
        for idx, field_input in enumerate(fields_data):
            if not isinstance(field_input, dict):
                continue
            field_identity = self._field_identity(field_input)
            existing_field = existing_fields.get(field_identity) if field_identity is not None else None
            existing_id = getattr(existing_field, "id", None)
            field_id = field_input.get("id") or field_input.get("field_id") or existing_id or _new_identifier()
            await self.field_repo.create({
                "id": field_id,
                "dataset_group_id": group_id,
                "origin_name": field_input.get("originName", field_input.get("origin_name", "")),
                "name": field_input.get("name"),
                "dataease_name": field_input.get("dataeaseName"),
                "field_short_name": field_input.get("fieldShortName"),
                "group_type": field_input.get("groupType"),
                "type": field_input.get("type", "VARCHAR"),
                "size": field_input.get("size"),
                "de_type": field_input.get("deType", 0),
                "de_extract_type": field_input.get("deExtractType", 0),
                "ext_field": field_input.get("extField", 0),
                "checked": field_input.get("checked", True),
                "column_index": field_input.get("columnIndex", idx),
                "accuracy": field_input.get("accuracy"),
                "date_format": field_input.get("dateFormat"),
                "date_format_type": field_input.get("dateFormatType"),
                "group_list": field_input.get("groupList", field_input.get("group_list")),
                "other_group": field_input.get("otherGroup", field_input.get("other_group")),
                "datasource_id": field_input.get("datasourceId", field_input.get("datasource_id")),
                "dataset_table_id": field_input.get("datasetTableId", field_input.get("dataset_table_id")),
            })

    async def _sync_dataset_source(self, group_id: int, group_name: str, info: object) -> CoreDatasetTable | None:
        info = self._normalize_info(info)
        if not isinstance(info, dict):
            return None
        datasource_id = info.get("datasourceId") or info.get("datasource_id")
        table_name = info.get("table") or info.get("tableName") or info.get("table_name")
        if datasource_id is None or not isinstance(table_name, str) or not table_name.strip():
            return None

        datasource_id_int = int(str(datasource_id))
        table_name_str = table_name.strip()
        dataset_table = await self._get_or_create_dataset_table(group_id, group_name, datasource_id_int, table_name_str)

        sql = info.get("sql")
        if isinstance(sql, str) and sql.strip():
            return dataset_table

        await self.field_repo.delete_by_group(group_id)
        fields = await self._load_datasource_fields(datasource_id_int, table_name_str)
        normalized_fields = [self._field_to_storage_payload(field, datasource_id_int, dataset_table.id) for field in fields]
        await self._save_fields_for_group(group_id, normalized_fields)
        return dataset_table

    async def _get_or_create_dataset_table(
        self,
        group_id: int,
        group_name: str,
        datasource_id: int,
        table_name: str,
    ) -> CoreDatasetTable:
        existing_tables = await self.table_repo.list_by_group(group_id)
        existing = next((table for table in existing_tables if table.table_name == table_name), None)
        if existing is not None:
            return existing
        return await self.table_repo.create({
            "id": _new_identifier(),
            "name": group_name,
            "table_name": table_name,
            "datasource_id": datasource_id,
            "dataset_group_id": group_id,
            "type": "db",
            "info": None,
        })

    async def _load_datasource_fields(self, datasource_id: int, table_name: str) -> list[DatasourceFieldResponse]:
        datasource = await DatasourceRepository(self.session).get_by_id(datasource_id)
        if datasource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")
        service = DatasourceService(self.session, DatasourceRepository(self.session))
        return await service.get_fields(datasource_id, table_name)

    @staticmethod
    def _build_dataset_sql_static(group: CoreDatasetGroup) -> str | None:
        if group.union_sql and str(group.union_sql).strip():
            return str(group.union_sql).strip()
        info = group.info
        if isinstance(info, dict):
            sql = info.get("sql")
            if isinstance(sql, str) and sql.strip():
                return sql.strip()
            table_name = info.get("table") or info.get("tableName") or info.get("table_name")
            if isinstance(table_name, str) and table_name.strip():
                safe = table_name.strip()
                if not _SAFE_IDENTIFIER_RE.match(safe):
                    return None
                return f'SELECT * FROM "{safe}"'
        return None

    async def _build_dataset_sql(self, group: CoreDatasetGroup) -> str | None:
        result = self._build_dataset_sql_static(group)
        if result is not None:
            return result
        tables = list(await self.table_repo.list_by_group(group.id))
        for t in tables:
            if t.table_name and t.table_name.strip():
                safe = t.table_name.strip()
                if _SAFE_IDENTIFIER_RE.match(safe):
                    return f'SELECT * FROM "{safe}"'
        return None

    def _build_sql_from_union(self, union_data: Sequence[object]) -> str | None:
        first_node = union_data[0] if union_data else None
        if not isinstance(first_node, dict):
            return None
        current_ds = first_node.get("currentDs")
        if not isinstance(current_ds, dict):
            return None

        ds_type = str(current_ds.get("type") or "").strip()
        if ds_type.lower() in {"db", "table"}:
            table_name = current_ds.get("tableName") or current_ds.get("table_name")
            if not isinstance(table_name, str) or not table_name.strip():
                return None
            return f"SELECT * FROM {self._quote_identifier(table_name.strip())}"

        if ds_type.lower() == "sql":
            info = self._normalize_info(current_ds.get("info"))
            if isinstance(info, dict):
                sql = info.get("sql")
                if isinstance(sql, str) and sql.strip():
                    return sql.strip()

        return None

    async def _execute_dataset_sql(self, sql: str, dataset_group_id: int) -> dict[str, object]:
        tables = list(await self.table_repo.list_by_group(dataset_group_id))
        datasource = await self._resolve_datasource_for_dataset(tables)

        if datasource is not None:
            return await self._execute_sql_for_datasource(sql, datasource.id)

        return await self.sql_executor.execute_select(sql, limit=1000)

    async def _preview_file_dataset_data(
        self,
        group: CoreDatasetGroup,
        dataset_group_id: int,
        limit: int,
        offset: int,
    ) -> dict[str, object] | None:
        datasource, table_name = await self._resolve_dataset_source(group, dataset_group_id)
        if datasource is None or not DatasourceService._is_file_type(datasource.type):
            return None
        return await self._load_file_preview_data(datasource, table_name, limit, offset)

    async def _preview_file_union_data(
        self,
        union_data: Sequence[object],
        limit: int,
        offset: int,
    ) -> dict[str, object] | None:
        datasource_id, table_name = self._resolve_union_source(union_data)
        if datasource_id is None:
            return None

        datasource = await DatasourceRepository(self.session).get_by_id(datasource_id)
        if datasource is None or not DatasourceService._is_file_type(datasource.type):
            return None

        return await self._load_file_preview_data(datasource, table_name, limit, offset)

    async def _load_file_preview_data(
        self,
        datasource: CoreDatasource,
        table_name: str | None,
        limit: int,
        offset: int,
    ) -> dict[str, object]:
        if not table_name:
            return {"fields": [], "data": [], "total": 0}

        ds_service = DatasourceService(self.session, DatasourceRepository(self.session))
        preview = await ds_service.preview_data({"datasourceId": datasource.id, "tableName": table_name})
        data_payload = preview.get("data")
        if not isinstance(data_payload, dict):
            return {"fields": [], "data": [], "total": 0}

        raw_fields = data_payload.get("fields")
        fields = cast(list[object], raw_fields) if isinstance(raw_fields, list) else []
        raw_rows = data_payload.get("data")
        rows = cast(list[object], raw_rows) if isinstance(raw_rows, list) else []
        sliced_rows = rows[offset: offset + limit]
        return {"fields": fields, "data": sliced_rows, "total": len(rows)}

    async def _execute_sql_for_datasource(self, sql: str, datasource_id: int) -> dict[str, object]:
        datasource = await DatasourceRepository(self.session).get_by_id(datasource_id)
        if datasource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")

        ds_service = DatasourceService(self.session, DatasourceRepository(self.session))
        config = datasource.configuration
        if isinstance(config, str):
            config = json.loads(config)
        connection = await ds_service._open_connection(_as_config_dict(config), ds_type=datasource.type)
        try:
            records = await connection.fetch(sql)
        finally:
            await connection.close()
        rows = [list(record) for record in records]
        fields = self._build_external_fields(records, rows)
        return {"sql": sql, "fields": fields, "data": rows, "total": len(rows)}

    def _extract_union_datasource_id(self, union_data: Sequence[object]) -> int | None:
        datasource_id, _ = self._resolve_union_source(union_data)
        return datasource_id

    @classmethod
    def _resolve_union_source(
        cls, union_data: Sequence[object]
    ) -> tuple[int | None, str | None]:
        first_node = union_data[0] if union_data else None
        if not isinstance(first_node, dict):
            return None, None
        current_ds = first_node.get("currentDs")
        if not isinstance(current_ds, dict):
            return None, None

        datasource_id_raw = current_ds.get("datasourceId") or current_ds.get("datasource_id")
        try:
            datasource_id = int(str(datasource_id_raw)) if datasource_id_raw is not None else None
        except (TypeError, ValueError):
            datasource_id = None

        table_name_raw = current_ds.get("tableName") or current_ds.get("table_name")
        table_name = table_name_raw.strip() if isinstance(table_name_raw, str) and table_name_raw.strip() else None
        if table_name is None:
            info = cls._normalize_info(current_ds.get("info"))
            if isinstance(info, dict):
                info_table_name = info.get("table") or info.get("tableName") or info.get("table_name")
                if isinstance(info_table_name, str) and info_table_name.strip():
                    table_name = info_table_name.strip()

        return datasource_id, table_name

    @staticmethod
    def _attach_union_to_info(info: object, union_data: Sequence[object] | None) -> object:
        if union_data is None:
            return info
        if isinstance(info, dict):
            payload = dict(info)
            payload["union"] = list(union_data)
            return payload
        return {"union": list(union_data)}

    def _build_detail_union(
        self,
        group: CoreDatasetGroup,
        tables: Sequence[CoreDatasetTable],
        fields: Sequence[CoreDatasetTableField],
    ) -> list[dict[str, object]]:
        info = self._normalize_info(group.info)
        if isinstance(info, dict):
            stored_union = info.get("union")
            if isinstance(stored_union, list):
                return cast(list[dict[str, object]], stored_union)

        if not tables:
            return []

        fields_by_table: dict[int, list[dict[str, object]]] = {}
        fallback_fields = [self._field_to_dict(field) for field in fields]
        for field in fields:
            if field.dataset_table_id is None:
                continue
            fields_by_table.setdefault(field.dataset_table_id, []).append(self._field_to_dict(field))

        nodes: list[dict[str, object]] = []
        for index, table in enumerate(tables):
            info_payload: dict[str, object] = {
                "table": table.table_name or "",
                "sql": "",
            }
            if table.datasource_id is not None:
                info_payload["datasourceId"] = _sid(table.datasource_id)
            if table.info:
                normalized_table_info = self._normalize_info(table.info)
                if isinstance(normalized_table_info, dict):
                    info_payload.update(cast(dict[str, object], normalized_table_info))

            table_fields = fields_by_table.get(table.id)
            if table_fields is None and index == 0:
                table_fields = fallback_fields

            nodes.append({
                "currentDs": {
                    "id": _sid(table.id),
                    "datasourceId": _sid(table.datasource_id),
                    "tableName": table.table_name,
                    "type": table.type,
                    "info": json.dumps(info_payload),
                    "sqlVariableDetails": table.sql_variable_details,
                },
                "currentDsFields": table_fields or [],
                "childrenDs": [],
                "unionToParent": None,
            })

        return nodes

    @classmethod
    def _resolve_source_payload(
        cls,
        info: object,
        datasource_id: int | None,
        table_name: str | None,
        union_data: Sequence[object] | None,
    ) -> tuple[int | None, str | None, object]:
        normalized_info = cls._normalize_info(info)
        resolved_datasource_id = datasource_id
        resolved_table_name = table_name
        resolved_info = normalized_info

        if resolved_datasource_id is None or resolved_table_name is None:
            union_datasource_id, union_table_name, union_info = cls._extract_source_from_union(union_data)
            if resolved_datasource_id is None:
                resolved_datasource_id = union_datasource_id
            if resolved_table_name is None:
                resolved_table_name = union_table_name
            if not isinstance(resolved_info, dict) and union_info is not None:
                resolved_info = union_info

        return resolved_datasource_id, resolved_table_name, resolved_info

    @classmethod
    def _extract_source_from_union(
        cls, union_data: Sequence[object] | None
    ) -> tuple[int | None, str | None, object | None]:
        first_node = union_data[0] if union_data else None
        if not isinstance(first_node, dict):
            return None, None, None
        current_ds = first_node.get("currentDs")
        if not isinstance(current_ds, dict):
            return None, None, None

        datasource_id_raw = current_ds.get("datasourceId") or current_ds.get("datasource_id")
        try:
            datasource_id = int(str(datasource_id_raw)) if datasource_id_raw is not None else None
        except (TypeError, ValueError):
            datasource_id = None

        table_name_raw = current_ds.get("tableName") or current_ds.get("table_name")
        table_name = table_name_raw.strip() if isinstance(table_name_raw, str) and table_name_raw.strip() else None
        info = cls._normalize_info(current_ds.get("info"))

        return datasource_id, table_name, info

    async def _resolve_datasource_for_dataset(self, tables: Sequence[object]) -> CoreDatasource | None:
        first_table = tables[0] if tables else None
        datasource_id = getattr(first_table, "datasource_id", None)
        if not isinstance(datasource_id, int):
            return None
        return await DatasourceRepository(self.session).get_by_id(datasource_id)

    async def _resolve_dataset_source(
        self,
        group: CoreDatasetGroup,
        dataset_group_id: int,
    ) -> tuple[CoreDatasource | None, str | None]:
        table_name: str | None = None
        info = self._normalize_info(group.info)
        if isinstance(info, dict):
            raw_table_name = info.get("table") or info.get("tableName") or info.get("table_name")
            if isinstance(raw_table_name, str) and raw_table_name.strip():
                table_name = raw_table_name.strip()

        tables = list(await self.table_repo.list_by_group(dataset_group_id))
        first_table = tables[0] if tables else None
        if table_name is None:
            raw_table_name = getattr(first_table, "table_name", None)
            if isinstance(raw_table_name, str) and raw_table_name.strip():
                table_name = raw_table_name.strip()

        datasource = await self._resolve_datasource_for_dataset(tables)
        if datasource is not None:
            return datasource, table_name

        datasource_id: int | None = None
        if isinstance(info, dict):
            raw_datasource_id = info.get("datasourceId") or info.get("datasource_id")
            try:
                datasource_id = int(str(raw_datasource_id)) if raw_datasource_id is not None else None
            except (TypeError, ValueError):
                datasource_id = None
        if datasource_id is None:
            return None, table_name
        return await DatasourceRepository(self.session).get_by_id(datasource_id), table_name

    @staticmethod
    def _field_to_storage_payload(field: DatasourceFieldResponse, datasource_id: int, dataset_table_id: int) -> dict[str, object]:
        name = getattr(field, "name", "")
        data_type = str(getattr(field, "data_type", "varchar") or "varchar")
        return {
            "originName": name,
            "name": name,
            "dataeaseName": name,
            "fieldShortName": name,
            "groupType": "d",
            "type": data_type,
            "deType": DatasetService._de_type_for_column(data_type),
            "deExtractType": 0,
            "extField": 0,
            "checked": True,
            "datasourceId": datasource_id,
            "datasetTableId": dataset_table_id,
        }

    @staticmethod
    def _normalize_fields_for_dataset_table(
        fields_data: Sequence[object] | None,
        dataset_table: CoreDatasetTable | None,
    ) -> Sequence[object]:
        if dataset_table is None:
            return fields_data or []

        normalized_fields: list[object] = []
        for field_input in fields_data or []:
            if not isinstance(field_input, dict):
                normalized_fields.append(field_input)
                continue
            payload = dict(field_input)
            payload["datasetTableId"] = dataset_table.id
            payload["dataset_table_id"] = dataset_table.id
            payload["datasourceId"] = dataset_table.datasource_id
            payload["datasource_id"] = dataset_table.datasource_id
            normalized_fields.append(payload)
        return normalized_fields

    @staticmethod
    def _datasource_field_to_response_dict(
        field: DatasourceFieldResponse, datasource_id: int, idx: int,
    ) -> dict[str, object]:
        data_type = str(getattr(field, "data_type", "varchar") or "varchar")
        return {
            "id": 0,
            "originName": field.origin_name,
            "name": field.name,
            "dataeaseName": field.name,
            "fieldShortName": field.name,
            "groupType": "d",
            "type": field.type or data_type,
            "size": None,
            "deType": field.de_type,
            "deExtractType": 0,
            "extField": 0,
            "checked": True,
            "columnIndex": idx,
            "accuracy": None,
            "dateFormat": None,
            "dateFormatType": None,
            "datasourceId": datasource_id,
            "datasetTableId": 0,
            "datasetGroupId": None,
            "chartId": None,
            "lastSyncTime": None,
            "description": None,
        }

    @staticmethod
    def _datasource_field_to_dataset_field(field: DatasourceFieldResponse, datasource_id: int) -> object:
        return type("DatasetFieldPayload", (), {
            "datasource_id": datasource_id,
            "origin_name": field.origin_name,
            "name": field.name,
            "type": field.type or str(getattr(field, "data_type", "varchar") or "varchar"),
            "de_type": field.de_type,
            "checked": True,
        })()

    @staticmethod
    def _normalize_info(info: object) -> object:
        if isinstance(info, str):
            try:
                return json.loads(info)
            except (TypeError, ValueError):
                return info
        return info

    @staticmethod
    def _merge_source_info(info: object, datasource_id: int | None, table_name: str | None) -> object:
        if datasource_id is None and table_name is None:
            return info
        payload: dict[str, object]
        if isinstance(info, dict):
            payload = dict(info)
        else:
            payload = {}
        if datasource_id is not None:
            payload["datasourceId"] = datasource_id
            payload["datasource_id"] = datasource_id
        if table_name is not None and table_name.strip():
            table_name_value = table_name.strip()
            payload["tableName"] = table_name_value
            payload["table_name"] = table_name_value
            payload["table"] = table_name_value
        return payload

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        cleaned = identifier.strip()
        if not cleaned:
            raise ValueError("SQL identifier must not be empty")
        if not _SAFE_IDENTIFIER_RE.match(cleaned):
            raise ValueError(f"Unsafe SQL identifier: {identifier}")
        return f'"{cleaned}"'

    @staticmethod
    def _de_type_for_column(data_type: str) -> int:
        lower = data_type.lower()
        if any(token in lower for token in ("int", "numeric", "decimal", "double", "real", "float")):
            return 1
        if any(token in lower for token in ("date", "time")):
            return 2
        return 0

    @staticmethod
    def _field_to_dict(field: object) -> dict[str, object]:
        return {
            "id": _sid(getattr(field, "id", None)),
            "originName": getattr(field, "origin_name", None),
            "name": getattr(field, "name", None),
            "dataeaseName": getattr(field, "dataease_name", None),
            "fieldShortName": getattr(field, "field_short_name", None),
            "groupType": getattr(field, "group_type", None),
            "type": getattr(field, "type", None),
            "size": getattr(field, "size", None),
            "deType": getattr(field, "de_type", None),
            "deExtractType": getattr(field, "de_extract_type", None),
            "extField": getattr(field, "ext_field", None),
            "checked": getattr(field, "checked", None),
            "columnIndex": getattr(field, "column_index", None),
            "accuracy": getattr(field, "accuracy", None),
            "dateFormat": getattr(field, "date_format", None),
            "dateFormatType": getattr(field, "date_format_type", None),
            "groupList": getattr(field, "group_list", None),
            "otherGroup": getattr(field, "other_group", None),
            "datasourceId": _sid(getattr(field, "datasource_id", None)),
            "datasetTableId": _sid(getattr(field, "dataset_table_id", None)),
        }

    @staticmethod
    def _field_identity(field: object) -> str | None:
        if isinstance(field, dict):
            ext_field = field.get("extField", field.get("ext_field"))
            dataset_table_id = field.get("datasetTableId", field.get("dataset_table_id"))
            origin_name = field.get("originName", field.get("origin_name"))
            name = field.get("name")
        else:
            ext_field = getattr(field, "ext_field", None)
            dataset_table_id = getattr(field, "dataset_table_id", None)
            origin_name = getattr(field, "origin_name", None)
            name = getattr(field, "name", None)

        ext_field_value = 0 if ext_field is None else int(ext_field)
        if ext_field_value in {0, 2}:
            if dataset_table_id is None or origin_name is None:
                return None
            return f"{dataset_table_id}:{origin_name}:{ext_field_value}"
        if name is None:
            return None
        return f"{name}:{ext_field_value}"

    @staticmethod
    def _field_to_preview_field(field: object) -> dict[str, object]:
        return {
            "name": getattr(field, "name", None) or getattr(field, "origin_name", None),
            "dataeaseName": getattr(field, "dataease_name", None),
            "originName": getattr(field, "origin_name", None),
            "type": getattr(field, "type", None),
            "deType": getattr(field, "de_type", None),
            "groupType": getattr(field, "group_type", None),
        }

    @staticmethod
    def _normalize_preview_all_fields(fields: Sequence[object] | None) -> list[dict[str, object]]:
        normalized: list[dict[str, object]] = []
        for field in fields or []:
            if not isinstance(field, dict):
                continue
            payload = dict(field)
            origin_name = payload.get("originName") or payload.get("origin_name") or payload.get("name")
            if origin_name is not None:
                payload["originName"] = origin_name
            normalized.append(payload)
        return normalized

    async def _filter_by_permission(
        self, groups: Sequence[CoreDatasetGroup]
    ) -> list[CoreDatasetGroup]:
        return list(groups)


async def get_dataset_service(session: AsyncSession = Depends(get_db)) -> DatasetService:
    return DatasetService(
        session=session,
        group_repo=DatasetGroupRepository(session),
        table_repo=DatasetTableRepository(session),
        field_repo=DatasetFieldRepository(session),
    )
