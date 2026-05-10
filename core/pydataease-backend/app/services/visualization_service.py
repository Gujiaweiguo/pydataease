from __future__ import annotations

import time
from typing import Any, cast, final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.visualization import DataVisualizationInfo
from app.repositories.chart_repo import ChartRepository
from app.repositories.store_repo import StoreRepository
from app.repositories.visualization_repo import VisualizationRepository
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
        return _build_tree(visible)

    async def find_by_id(self, payload: VisualizationFindByIdRequest) -> VisualizationResponse:
        item = await self._get_visualization(payload.id)
        return VisualizationResponse.model_validate(item)

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
        items = await self.visualization_repo.list_recent(payload.size)
        return [VisualizationResponse.model_validate(item) for item in items]

    async def per_resource(self, visualization_id: int) -> VisualizationResponse:
        item = await self._get_visualization(visualization_id)
        return VisualizationResponse.model_validate(item)

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

    async def _get_visualization(self, visualization_id: int) -> DataVisualizationInfo:
        item = await self.visualization_repo.get_by_id(visualization_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
        return item

    async def _read_meta(self, dv_id: int | None, view_id: int | None, key: str, resource_table: str | None = None) -> dict[str, object]:
        if dv_id is None:
            return {"dvId": None, "viewId": view_id, "resourceTable": resource_table, "config": []}
        item = await self._get_visualization(dv_id)
        component = cast(dict[str, object], item.component_data if isinstance(item.component_data, dict) else {})
        stored = component.get(key)
        if isinstance(stored, dict):
            return stored
        return {"dvId": dv_id, "viewId": view_id, "resourceTable": resource_table, "config": []}

    async def _write_meta(self, dv_id: int | None, view_id: int | None, key: str, value: dict[str, object]) -> dict[str, object]:
        if dv_id is None:
            return {"dvId": None, "viewId": view_id, **value}
        item = await self._get_visualization(dv_id)
        component = cast(dict[str, object], item.component_data if isinstance(item.component_data, dict) else {})
        payload = {"dvId": dv_id, "viewId": view_id, **value}
        component[key] = payload
        await self.visualization_repo.update(item, {"component_data": component, "update_time": _timestamp_ms()})
        return payload


async def get_visualization_service(session: AsyncSession = Depends(get_db)) -> VisualizationService:
    return VisualizationService(session)
