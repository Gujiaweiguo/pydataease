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
    VisualizationFindByIdRequest,
    VisualizationMoveRequest,
    VisualizationRecentRequest,
    VisualizationRenameRequest,
    VisualizationResponse,
    VisualizationSaveRequest,
    VisualizationTreeNodeResponse,
    VisualizationTreeRequest,
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

    async def tree(self, _: VisualizationTreeRequest) -> list[VisualizationTreeNodeResponse]:
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

    async def find_by_id(self, payload: VisualizationFindByIdRequest) -> VisualizationResponse:
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
        created = await self.visualization_repo.create({
            **payload.model_dump(by_alias=False, exclude_none=True),
            "id": payload.id or _new_identifier(),
            "level": _compute_level(items, payload.pid),
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
        new_pid = payload.pid if payload.pid is not None else existing.pid
        update_data = payload.model_dump(by_alias=False, exclude_none=True)
        update_data.update({
            "level": _compute_level(items, new_pid),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        updated = await self.visualization_repo.update(existing, update_data)
        return VisualizationResponse.model_validate(updated)

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
        updated = await self.visualization_repo.update(existing, {
            "pid": payload.pid,
            "level": _compute_level(items, payload.pid),
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

    async def per_resource(self, visualization_id: int) -> VisualizationResponse:
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
    ) -> dict:
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
