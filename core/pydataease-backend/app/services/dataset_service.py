from __future__ import annotations

import json
import time
from collections.abc import Sequence
from importlib import import_module
from typing import Any, final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.dataset import CoreDatasetGroup
from app.repositories.dataset_repo import (
    DatasetFieldRepository,
    DatasetGroupRepository,
    DatasetTableRepository,
)
from app.schemas.auth import TokenUser
from app.schemas.dataset import (
    DatasetFieldResponse,
    DatasetGroupCreate,
    DatasetGroupMove,
    DatasetGroupRename,
    DatasetGroupUpdate,
    DatasetNodeResponse,
    DatasetTableFieldRequest,
    DatasetTreeNodeResponse,
)

SQLExecutor = import_module("app.services.sql_executor").SQLExecutor


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

    async def tree(self) -> list[dict]:
        groups = await self.group_repo.list_all_ordered()
        groups = await self._filter_by_permission(groups)
        built_tree = _build_tree(list(groups))

        def _node_to_dict(node: DatasetTreeNodeResponse) -> dict:
            d = node.model_dump()
            d["weight"] = 9
            d["extraFlag"] = 0
            d["extraFlag1"] = 0
            d["children"] = [_node_to_dict(c) for c in (node.children or [])]
            return d

        children = [_node_to_dict(n) for n in built_tree]
        root = {
            "id": 0,
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
        info_str = json.dumps(payload.info) if payload.info is not None else None

        created = await self.group_repo.create({
            "id": _new_identifier(),
            "name": payload.name.strip(),
            "pid": pid_value,
            "level": level,
            "node_type": payload.node_type,
            "type": payload.type,
            "mode": payload.mode,
            "info": info_str,
            "create_by": str(user.user_id),
            "create_time": now,
            "update_by": str(user.user_id),
            "last_update_time": now,
            "is_cross": payload.is_cross,
        })

        if payload.all_fields:
            await self._save_fields_for_group(created.id, payload.all_fields)

        return DatasetNodeResponse.model_validate(created)

    async def save(self, payload: DatasetGroupUpdate, user: TokenUser) -> DatasetNodeResponse:
        existing = await self._get_group(payload.id)

        all_groups = list(await self.group_repo.list_all_ordered())
        raw_pid = payload.pid if payload.pid is not None else existing.pid
        new_pid = None if raw_pid == 0 else raw_pid
        level = _compute_level(all_groups, new_pid)

        now = _timestamp_ms()
        info_value = payload.info if payload.info is not None else existing.info
        info_str = json.dumps(info_value) if isinstance(info_value, (dict, list)) else info_value

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
        if info_str is not None:
            update_data["info"] = info_str
        if payload.is_cross is not None:
            update_data["is_cross"] = payload.is_cross

        updated = await self.group_repo.update(existing, update_data)

        if payload.all_fields is not None:
            await self.field_repo.delete_by_group(payload.id)
            await self._save_fields_for_group(payload.id, payload.all_fields)

        return DatasetNodeResponse.model_validate(updated)

    async def rename(self, payload: DatasetGroupRename, user: TokenUser) -> DatasetNodeResponse:
        existing = await self._get_group(payload.id)
        updated = await self.group_repo.update(existing, {
            "name": payload.name.strip(),
            "update_by": str(user.user_id),
            "last_update_time": _timestamp_ms(),
        })
        return DatasetNodeResponse.model_validate(updated)

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
        return DatasetNodeResponse.model_validate(updated)

    async def delete(self, group_id: int) -> None:
        await self._get_group(group_id)
        await self.group_repo.delete_cascade(group_id)

    async def get_bar_info(self, group_id: int) -> DatasetNodeResponse:
        group = await self._get_group(group_id)
        return DatasetNodeResponse.model_validate(group)

    async def get_details(self, group_id: int) -> DatasetNodeResponse:
        group = await self._get_group(group_id)
        return DatasetNodeResponse.model_validate(group)

    async def get_fields(self, request: DatasetTableFieldRequest) -> list[DatasetFieldResponse]:
        if request.dataset_group_id:
            fields = await self.field_repo.list_by_group(request.dataset_group_id)
        elif request.datasource_id:
            stmt_fields = await self.field_repo.list_by_table(request.datasource_id)
            fields = stmt_fields
        else:
            fields = []
        return [DatasetFieldResponse.model_validate(f) for f in fields]

    async def preview_sql(self, sql: str) -> dict[str, object]:
        return await self.sql_executor.execute_select(sql)

    async def preview_sql_stub(self, sql: str) -> dict[str, object]:
        return await self.preview_sql(sql)

    async def per_delete(self, group_id: int) -> bool:
        group = await self.group_repo.get_by_id(group_id)
        return group is not None

    async def _get_group(self, group_id: int) -> CoreDatasetGroup:
        group = await self.group_repo.get_by_id(group_id)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        return group

    async def _save_fields_for_group(self, group_id: int, fields_data: list[object]) -> None:
        for idx, field_input in enumerate(fields_data):
            if not isinstance(field_input, dict):
                continue
            await self.field_repo.create({
                "id": _new_identifier(),
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
                "datasource_id": field_input.get("datasourceId", field_input.get("datasource_id")),
                "dataset_table_id": field_input.get("datasetTableId", field_input.get("dataset_table_id")),
            })

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
