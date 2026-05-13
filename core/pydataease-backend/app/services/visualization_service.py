from __future__ import annotations

import json as _json
import time
from typing import Any, cast, final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.chart import CoreChartView
from app.models.visualization import DataVisualizationInfo
from app.repositories.chart_repo import ChartRepository
from app.repositories.store_repo import StoreRepository
from app.repositories.visualization_repo import VisualizationRepository
from app.utils.id_utils import _sid
from app.schemas.auth import TokenUser
from app.schemas.chart import ChartResponse
from app.schemas.visualization import (
    JumpRequest,
    LinkageRequest,
    OuterParamsRequest,
    StoreResponse,
    VisualizationAppCanvasNameCheckRequest,
    VisualizationCanvasChangeRequest,
    VisualizationCanvasRequest,
    VisualizationDeleteLogicRequest,
    VisualizationDecompressionRequest,
    VisualizationFindByIdRequest,
    VisualizationMoveRequest,
    VisualizationNameCheckRequest,
    VisualizationPublishStatusRequest,
    VisualizationRecentRequest,
    VisualizationRenameRequest,
    VisualizationResponse,
    VisualizationSaveRequest,
    VisualizationTreeNodeResponse,
    VisualizationTreeRequest,
    VisualizationUpdateBaseRequest,
    VisualizationUpdateRequest,
)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


def _compute_level(all_items: list[DataVisualizationInfo], pid: int | None) -> int:
    if pid is None or pid == 0:
        return 0
    id_to_level = {item.id: item.level or 0 for item in all_items}
    return (id_to_level.get(pid, 0) or 0) + 1


def _parse_json_value(value: str | None) -> object | None:
    if value is None:
        return None
    try:
        return _json.loads(value)
    except (TypeError, ValueError):
        return value


def _normalize_int(value: int | str | None) -> int | None:
    """Normalize an int/str/None value. Returns None for 0, empty, or null (root-level pid)."""
    if value in (None, "", "null", 0, "0"):
        return None
    return int(value)


def _build_tree(items: list[DataVisualizationInfo]) -> list[VisualizationTreeNodeResponse]:
    nodes: dict[int, VisualizationTreeNodeResponse] = {}
    for item in items:
        node = VisualizationTreeNodeResponse.model_validate(item)
        node.leaf = item.node_type == "leaf"
        node.children = []
        nodes[item.id] = node
    roots: list[VisualizationTreeNodeResponse] = []
    for item in items:
        node = nodes[item.id]
        if item.pid in (None, 0) or item.pid not in nodes:
            roots.append(node)
        else:
            nodes[item.pid].children.append(node)
    return roots


@final
class VisualizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.visualization_repo = VisualizationRepository(session)
        self.store_repo = StoreRepository(session)
        self.chart_repo = ChartRepository(session)

    async def tree(self, _: VisualizationTreeRequest) -> object:
        items = await self.visualization_repo.list_all_ordered()
        visible = [item for item in items if not item.delete_flag]
        nodes = _build_tree(visible)

        def _node_to_dict(node: VisualizationTreeNodeResponse) -> dict[str, object]:
            data = node.model_dump(by_alias=True)
            data["id"] = _sid(data.get("id"))
            data["pid"] = _sid(data.get("pid"))
            data["children"] = [_node_to_dict(child) for child in node.children]
            return data

        return [_node_to_dict(node) for node in nodes]  # type: ignore[return-value]

    async def find_by_id(self, payload: VisualizationFindByIdRequest) -> object:
        item = await self._get_visualization(payload.id)
        result = self._serialize_visualization(item)
        # Attach canvasViewInfo — map of chartId -> chart view details
        charts = await self.chart_repo.list_by_scene(payload.id)
        view_info: dict[str, object] = {}
        for chart in charts:
            chart_dict: dict[str, object] = {}
            for col in CoreChartView.__table__.columns:
                val = getattr(chart, col.name, None)
                if col.name == "id":
                    chart_dict["id"] = _sid(val)
                else:
                    chart_dict[col.name] = val
            # Parse JSON string fields that frontend expects as objects
            for json_field in ("custom_attr", "custom_style", "custom_filter", "senior", "x_axis", "y_axis", "x_axis_ext", "y_axis_ext", "ext_stack", "ext_bubble", "ext_label", "ext_tooltip", "drill_fields", "view_fields", "ext_color"):
                raw = chart_dict.get(json_field)
                if isinstance(raw, str):
                    try:
                        chart_dict[json_field] = _json.loads(raw)
                    except (ValueError, TypeError):
                        pass
            view_info[str(chart.id)] = chart_dict
        result["canvasViewInfo"] = view_info
        return result  # type: ignore[return-value]

    async def save(self, payload: VisualizationSaveRequest, user: TokenUser) -> VisualizationResponse:
        items = list(await self.visualization_repo.list_all_ordered())
        now = _timestamp_ms()
        pid = _normalize_int(payload.pid)
        created = await self.visualization_repo.create({
            **payload.model_dump(by_alias=False, exclude_none=True),
            "id": payload.id or _new_identifier(),
            "pid": pid,
            "level": _compute_level(items, pid),
            "create_time": now,
            "create_by": str(user.user_id),
            "update_time": now,
            "update_by": str(user.user_id),
            "delete_flag": bool(payload.delete_flag) if payload.delete_flag is not None else False,
        })
        return VisualizationResponse.model_validate(created)

    async def update(self, payload: VisualizationUpdateRequest, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        new_pid = _normalize_int(payload.pid) if payload.pid is not None else existing.pid
        update_data = payload.model_dump(by_alias=False, exclude_none=True)
        update_data.update({
            "pid": new_pid,
            "level": _compute_level(items, new_pid),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        updated = await self.visualization_repo.update(existing, update_data)
        return VisualizationResponse.model_validate(updated)

    async def save_canvas(self, payload: VisualizationCanvasRequest, user: TokenUser) -> dict[str, object]:
        items = list(await self.visualization_repo.list_all_ordered())
        now = _timestamp_ms()
        visualization_id = payload.id or _new_identifier()
        pid = _normalize_int(payload.pid)
        existing = await self.visualization_repo.get_by_id(visualization_id)
        if existing is None:
            created = await self.visualization_repo.create({
                "id": visualization_id,
                "name": payload.name,
                "pid": pid,
                "level": _compute_level(items, pid),
                "node_type": "leaf",
                "type": payload.type,
                "canvas_style_data": _parse_json_value(payload.canvas_style_data),
                "component_data": self._merge_component_state(_parse_json_value(payload.component_data), None),
                "mobile_layout": payload.mobile_layout,
                "status": payload.status if payload.status is not None else 0,
                "content_id": payload.content_id,
                "check_version": payload.check_version,
                "create_time": now,
                "create_by": str(user.user_id),
                "update_time": now,
                "update_by": str(user.user_id),
                "delete_flag": False,
            })
        else:
            created = await self.visualization_repo.update(existing, {
                "name": payload.name,
                "pid": pid if pid is not None else existing.pid,
                "level": _compute_level(items, pid if pid is not None else existing.pid),
                "node_type": existing.node_type or "leaf",
                "type": payload.type or existing.type,
                "canvas_style_data": _parse_json_value(payload.canvas_style_data),
                "component_data": self._merge_component_state(_parse_json_value(payload.component_data), existing.component_data),
                "mobile_layout": payload.mobile_layout if payload.mobile_layout is not None else existing.mobile_layout,
                "status": payload.status if payload.status is not None else existing.status,
                "content_id": payload.content_id if payload.content_id is not None else existing.content_id,
                "check_version": payload.check_version if payload.check_version is not None else existing.check_version,
                "update_time": now,
                "update_by": str(user.user_id),
            })
        await self._sync_canvas_views(created.id, payload.canvas_view_info, user, delete_missing=False)
        return {"id": _sid(created.id), "status": 0}

    async def update_canvas(self, payload: VisualizationCanvasRequest, user: TokenUser) -> dict[str, object]:
        if payload.id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visualization id is required")
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        pid = _normalize_int(payload.pid)
        component_data = self._merge_component_state(_parse_json_value(payload.component_data), existing.component_data)
        await self.visualization_repo.update(existing, {
            "name": payload.name,
            "pid": pid if pid is not None else existing.pid,
            "level": _compute_level(items, pid if pid is not None else existing.pid),
            "node_type": existing.node_type or "leaf",
            "type": payload.type or existing.type,
            "canvas_style_data": _parse_json_value(payload.canvas_style_data),
            "component_data": component_data,
            "mobile_layout": payload.mobile_layout,
            "status": 2,
            "content_id": payload.content_id,
            "check_version": payload.check_version,
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        await self._sync_canvas_views(existing.id, payload.canvas_view_info, user, delete_missing=True)
        return {"status": 2}

    async def update_base(self, payload: VisualizationUpdateBaseRequest, user: TokenUser) -> dict[str, object]:
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        pid = _normalize_int(payload.pid)
        updated = await self.visualization_repo.update(existing, {
            "name": payload.name.strip() if payload.name else existing.name,
            "pid": pid if pid is not None else existing.pid,
            "level": _compute_level(items, pid if pid is not None else existing.pid),
            "node_type": payload.node_type or existing.node_type,
            "type": payload.type or existing.type,
            "mobile_layout": payload.mobile_layout if payload.mobile_layout is not None else existing.mobile_layout,
            "status": payload.status if payload.status is not None else existing.status,
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return self._serialize_visualization(updated)

    async def update_publish_status(self, payload: VisualizationPublishStatusRequest, user: TokenUser) -> dict[str, object]:
        existing = await self._get_visualization(payload.id)
        component_data = self._merge_component_state(existing.component_data, existing.component_data, payload.active_view_ids)
        updated = await self.visualization_repo.update(existing, {
            "status": payload.status,
            "component_data": component_data,
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return {"id": _sid(updated.id), "status": updated.status}

    async def name_check(self, payload: VisualizationNameCheckRequest) -> bool:
        pid = _normalize_int(payload.pid)
        normalized_name = payload.name.strip()
        items = await self.visualization_repo.list_all_ordered()
        for item in items:
            if item.delete_flag:
                continue
            if (item.pid) != pid:
                continue
            if (item.name or "").strip() != normalized_name:
                continue
            if payload.type and item.type != payload.type:
                continue
            if payload.opt == "edit" and payload.id is not None and item.id == payload.id:
                continue
            return False
        return True

    async def check_canvas_change(self, payload: VisualizationCanvasChangeRequest) -> str:
        existing = await self._get_visualization(payload.id)
        if payload.content_id and existing.content_id and payload.content_id != existing.content_id:
            return "Repeat"
        if payload.check_version and existing.check_version and payload.check_version != existing.check_version:
            return "Repeat"
        return "NoChange"

    async def recover_to_published(self, payload: VisualizationFindByIdRequest) -> object:
        return await self.find_by_id(payload)

    async def delete_logic(self, payload: VisualizationDeleteLogicRequest, user: TokenUser) -> dict[str, object]:
        deleted = await self.delete(payload.dv_id, user)
        return self._serialize_visualization(await self._get_visualization(payload.dv_id))

    async def find_copy_resource(self, dv_id: int, busi_flag: str) -> object:
        return await self.find_by_id(VisualizationFindByIdRequest(id=dv_id, busi_flag=busi_flag))

    async def app_canvas_name_check(self, _: VisualizationAppCanvasNameCheckRequest) -> str:
        return "success"

    async def decompression(self, payload: dict[str, object] | VisualizationDecompressionRequest) -> dict[str, object]:
        if isinstance(payload, VisualizationDecompressionRequest):
            return payload.data
        return payload

    async def delete(self, visualization_id: int, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(visualization_id)
        updated = await self.visualization_repo.update(existing, {
            "delete_flag": True,
            "delete_time": _timestamp_ms(),
            "delete_by": str(user.user_id),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return VisualizationResponse.model_validate(updated)

    async def move(self, payload: VisualizationMoveRequest, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        pid = _normalize_int(payload.pid)
        updated = await self.visualization_repo.update(existing, {
            "pid": pid,
            "level": _compute_level(items, pid),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return VisualizationResponse.model_validate(updated)

    async def rename(self, payload: VisualizationRenameRequest, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(payload.id)
        updated = await self.visualization_repo.update(existing, {
            "name": payload.name.strip(),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return VisualizationResponse.model_validate(updated)

    async def find_recent(self, payload: VisualizationRecentRequest) -> list[VisualizationResponse]:
        items = await self.visualization_repo.list_recent(
            size=payload.size,
            type_filter=payload.type,
            keyword=payload.keyword,
            asc=payload.asc,
        )
        return [VisualizationResponse.model_validate(item) for item in items]

    async def per_resource(self, visualization_id: int) -> object:
        item = await self._get_visualization(visualization_id)
        return self._serialize_visualization(item)  # type: ignore[return-value]

    async def view_detail_list(self, visualization_id: int) -> list[ChartResponse]:
        charts = await self.chart_repo.list_by_scene(visualization_id)
        return [ChartResponse.model_validate(chart) for chart in charts]

    async def favorited(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        item = await self.store_repo.get_by_resource(resource_id, user.user_id, resource_type)
        return StoreResponse(resource_id=resource_id, favorited=item is not None)

    async def add_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        existing = await self.store_repo.get_by_resource(resource_id, user.user_id, resource_type)
        if existing is None:
            await self.store_repo.create({
                "id": _new_identifier(),
                "resource_id": resource_id,
                "uid": user.user_id,
                "resource_type": resource_type,
                "time": _timestamp_ms(),
            })
        return StoreResponse(resource_id=resource_id, favorited=True)

    async def remove_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        await self.store_repo.delete_by_resource(resource_id, user.user_id, resource_type)
        return StoreResponse(resource_id=resource_id, favorited=False)

    async def query_stores(
        self,
        user: TokenUser,
        keyword: str | None = None,
        type_filter: str | None = None,
        asc: bool | None = None,
    ) -> dict[str, object]:
        """Query favorited items for the current user, joined with visualization info."""
        resource_type = None
        if type_filter == "panel":
            resource_type = 1
        elif type_filter == "screen":
            resource_type = 2

        try:
            stores = await self.store_repo.query_by_user(user.user_id, resource_type)
        except (AttributeError, TypeError):
            return {"totalCount": 0, "list": []}

        result_list = []
        for store in stores:
            viz = await self.visualization_repo.get_by_id(store.resource_id)
            if viz is None or viz.delete_flag:
                continue
            if keyword and keyword.lower() not in (viz.name or "").lower():
                continue
            result_list.append({
                "id": viz.id,
                "name": viz.name or "",
                "type": viz.type or "panel",
                "creator": viz.create_by or "",
                "lastEditor": viz.update_by or "",
                "lastEditTime": viz.update_time,
                "storeId": store.id,
                "resourceType": store.resource_type,
            })

        if asc:
            result_list.reverse()

        return {"totalCount": len(result_list), "list": result_list}

    async def get_view_linkage_gather(self, payload: LinkageRequest) -> dict[str, object]:
        return await self._read_meta(payload.dv_id, payload.view_id, "_linkage")

    async def get_view_linkage_gather_array(self, payload: LinkageRequest) -> list[object]:
        data = await self._read_meta(payload.dv_id, payload.view_id, "_linkage")
        config = data.get("config", [])
        return list(config) if isinstance(config, list) else []

    async def save_linkage(self, payload: LinkageRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_linkage", payload.model_dump(by_alias=True, exclude_none=True))

    async def get_visualization_all_linkage_info(self, dv_id: int, resource_table: str) -> dict[str, object]:
        return await self._read_meta(dv_id, None, "_linkage", resource_table)

    async def update_linkage_active(self, payload: LinkageRequest) -> dict[str, object]:
        current = await self._read_meta(payload.dv_id, payload.view_id, "_linkage")
        current["active"] = payload.active
        return await self._write_meta(payload.dv_id, payload.view_id, "_linkage", current)

    async def remove_linkage(self, payload: LinkageRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_linkage", {})

    async def get_table_field_with_view_id(self, view_id: int) -> list[object]:
        chart = await self.chart_repo.get_by_id(view_id)
        if chart is None:
            return []
        if isinstance(chart.view_fields, list):
            return chart.view_fields
        return []

    async def query_with_view_id(self, dv_id: int, view_id: int) -> dict[str, object]:
        return await self._read_meta(dv_id, view_id, "_jump")

    async def update_jump_set(self, payload: JumpRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_jump", payload.model_dump(by_alias=True, exclude_none=True))

    async def query_target_visualization_jump_info(self, payload: JumpRequest) -> dict[str, object]:
        return await self._read_meta(payload.target_dv_id or payload.dv_id, payload.view_id, "_jump")

    async def query_visualization_jump_info(self, dv_id: int, resource_table: str) -> dict[str, object]:
        return await self._read_meta(dv_id, None, "_jump", resource_table)

    async def update_jump_set_active(self, payload: JumpRequest) -> dict[str, object]:
        current = await self._read_meta(payload.dv_id, payload.view_id, "_jump")
        current["active"] = payload.active
        return await self._write_meta(payload.dv_id, payload.view_id, "_jump", current)

    async def remove_jump_set(self, payload: JumpRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_jump", {})

    async def query_with_visualization_id(self, dv_id: int) -> dict[str, object]:
        return await self._read_meta(dv_id, None, "_outerParams")

    async def update_outer_params_set(self, payload: OuterParamsRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, None, "_outerParams", payload.model_dump(by_alias=True, exclude_none=True))

    async def get_outer_params_info(self, dv_id: int) -> dict[str, object]:
        data = await self._read_meta(dv_id, None, "_outerParams")
        return {"dvId": dv_id, "params": data.get("params", [])}

    async def query_ds_with_visualization_id(self, dv_id: int) -> list[dict[str, Any]]:
        visualization = await self._get_visualization(dv_id)
        component_data = visualization.component_data if isinstance(visualization.component_data, dict | list) else None
        dataset_ids: list[dict[str, Any]] = []
        if isinstance(component_data, list):
            for item in component_data:
                if isinstance(item, dict) and item.get("datasetId") is not None:
                    dataset_ids.append({"datasetId": item.get("datasetId")})
        return dataset_ids

    async def find_dv_type(self, dv_id: int) -> str:
        item = await self.visualization_repo.get_by_id(dv_id)
        if item is None or item.type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
        return item.type

    async def update_check_version(self, dv_id: int) -> str:
        item = await self._get_visualization(dv_id)
        await self.visualization_repo.update(item, {"check_version": str(_timestamp_ms())})
        return ""

    async def save_watermark(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"success": True}

    async def _sync_canvas_views(
        self,
        visualization_id: int,
        canvas_view_info: dict[str, dict[str, object]],
        user: TokenUser,
        *,
        delete_missing: bool,
    ) -> None:
        now = _timestamp_ms()
        keep_ids: set[int] = set()
        for raw_view_id, chart_info in canvas_view_info.items():
            view_id = self._resolve_chart_id(raw_view_id, chart_info)
            keep_ids.add(view_id)
            existing = await self.chart_repo.get_by_id(view_id)
            chart_payload = self._build_chart_payload(chart_info, view_id, visualization_id, str(user.user_id), now, existing)
            await self.chart_repo.upsert_by_id(chart_payload)
        if delete_missing:
            await self.chart_repo.delete_by_scene_excluding(visualization_id, keep_ids)

    def _build_chart_payload(
        self,
        chart_info: dict[str, object],
        view_id: int,
        visualization_id: int,
        user_id: str,
        now: int,
        existing: CoreChartView | None,
    ) -> dict[str, object]:
        field_names = {column.name for column in CoreChartView.__table__.columns}
        payload: dict[str, object] = {
            "id": view_id,
            "scene_id": visualization_id,
            "update_time": now,
        }
        if existing is None:
            payload["create_time"] = now
            payload["create_by"] = user_id
        else:
            payload["create_time"] = existing.create_time
            payload["create_by"] = existing.create_by
        for key, value in chart_info.items():
            snake_key = self._camel_to_snake(key)
            if snake_key in {"id", "scene_id", "update_by"}:
                continue
            if snake_key in field_names:
                payload[snake_key] = value
        if "title" not in payload:
            payload["title"] = chart_info.get("title") or chart_info.get("name") or ""
        if "type" not in payload:
            payload["type"] = chart_info.get("type") or chart_info.get("chartType") or "bar"
        return payload

    @staticmethod
    def _resolve_chart_id(raw_view_id: str, chart_info: dict[str, object]) -> int:
        chart_id = chart_info.get("id", raw_view_id)
        if not isinstance(chart_id, (int, str)):
            raise TypeError("chart id must be int or str")
        return int(chart_id)

    @staticmethod
    def _camel_to_snake(value: str) -> str:
        chars: list[str] = []
        for char in value:
            if char.isupper():
                chars.extend(("_", char.lower()))
            else:
                chars.append(char)
        return "".join(chars).lstrip("_")

    @staticmethod
    def _merge_component_state(
        component_data: object | None,
        existing_component_data: object | None,
        active_view_ids: list[int] | None = None,
    ) -> object | None:
        if active_view_ids is None:
            if isinstance(component_data, list):
                return component_data
            if isinstance(component_data, dict):
                merged = dict(component_data)
                if isinstance(existing_component_data, dict) and "_activeViewIds" in existing_component_data and "_activeViewIds" not in merged:
                    merged["_activeViewIds"] = existing_component_data["_activeViewIds"]
                return merged
            return component_data

        if isinstance(component_data, dict):
            merged = dict(component_data)
        elif isinstance(existing_component_data, dict):
            merged = dict(existing_component_data)
        else:
            merged = {}
        merged["_activeViewIds"] = active_view_ids
        return merged

    async def _get_visualization(self, visualization_id: int) -> DataVisualizationInfo:
        item = await self.visualization_repo.get_by_id(visualization_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
        return item

    async def _read_meta(self, dv_id: int | None, view_id: int | None, key: str, resource_table: str | None = None) -> dict[str, object]:
        if dv_id is None:
            return {"dvId": None, "viewId": _sid(view_id), "resourceTable": resource_table, "config": []}
        item = await self._get_visualization(dv_id)
        component = cast(dict[str, object], item.component_data if isinstance(item.component_data, dict) else {})
        stored = component.get(key)
        if isinstance(stored, dict):
            return stored
        return {"dvId": _sid(dv_id), "viewId": _sid(view_id), "resourceTable": resource_table, "config": []}

    async def _write_meta(self, dv_id: int | None, view_id: int | None, key: str, value: dict[str, object]) -> dict[str, object]:
        if dv_id is None:
            return {"dvId": None, "viewId": _sid(view_id), **value}
        item = await self._get_visualization(dv_id)
        component = cast(dict[str, object], item.component_data if isinstance(item.component_data, dict) else {})
        payload = {"dvId": _sid(dv_id), "viewId": _sid(view_id), **value}
        component[key] = payload
        await self.visualization_repo.update(item, {"component_data": component, "update_time": _timestamp_ms()})
        return payload

    @staticmethod
    def _serialize_visualization(item: DataVisualizationInfo) -> dict[str, object]:
        payload = VisualizationResponse.model_validate(item).model_dump(by_alias=True)
        payload["id"] = _sid(payload.get("id"))
        payload["pid"] = _sid(payload.get("pid"))
        # Frontend expects JSON strings for these JSONB fields (Java backend stored as strings)
        for key in ("canvasStyleData", "componentData"):
            val = payload.get(key)
            if val is not None and not isinstance(val, str):
                payload[key] = _json.dumps(val, ensure_ascii=False)
        return payload


async def get_visualization_service(session: AsyncSession = Depends(get_db)) -> VisualizationService:
    return VisualizationService(session)
