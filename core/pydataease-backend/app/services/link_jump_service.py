from __future__ import annotations

import time
from collections import defaultdict
from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.visualization import DataVisualizationInfo
from app.repositories.link_jump_repo import LinkJumpFieldRepository, LinkJumpRepository
from app.schemas.link_jump import (
    DatasetTableFieldDTO,
    LinkJumpBaseRequest,
    LinkJumpBaseResponse,
    LinkJumpInfoDTO,
    LinkJumpTargetViewInfo,
    OutParamsJumpDTO,
    ViewTableDetailDTO,
    ViewTableFieldDTO,
    VisualizationComponentDTO,
    VisualizationLinkJumpDTO,
)


def _table_name(resource_table: str) -> str:
    """Map resourceTable to snapshot or core table prefix."""
    return "snapshot" if resource_table == "snapshot" else "core"


def _build_info_from_rows(rows: list[dict]) -> list[LinkJumpInfoDTO]:
    """Build LinkJumpInfoDTO list from raw SQL rows.

    The SQL returns one row per (info, target) combination because of the
    LEFT JOIN on target_view_info. We need to group by info ID.
    """
    info_map: dict[int, dict] = {}
    target_map: dict[int, list[LinkJumpTargetViewInfo]] = defaultdict(list)

    for row in rows:
        info_id = row.get("id")
        if info_id is None:
            continue
        if info_id not in info_map:
            info_map[info_id] = {
                "id": info_id,
                "link_jump_id": row.get("link_jump_id"),
                "link_type": row.get("link_type"),
                "jump_type": row.get("jump_type"),
                "window_size": row.get("window_size"),
                "target_dv_id": row.get("target_dv_id"),
                "source_field_id": row.get("source_field_id"),
                "content": row.get("content"),
                "checked": row.get("checked"),
                "attach_params": row.get("attach_params"),
                "source_field_name": row.get("source_field_name"),
                "source_de_type": row.get("source_de_type"),
                "target_dv_type": row.get("target_dv_type"),
            }
        target_id = row.get("target_id")
        if target_id is not None:
            target_map[info_id].append(
                LinkJumpTargetViewInfo(
                    target_id=target_id,
                    link_jump_info_id=info_id,
                    source_field_active_id=row.get("source_field_active_id"),
                    target_view_id=str(row.get("target_view_id", "")),
                    target_field_id=str(row.get("target_field_id", "")),
                    target_type=row.get("target_type"),
                    outer_params_name=row.get("outer_params_name"),
                )
            )

    result: list[LinkJumpInfoDTO] = []
    for info_id, info_data in info_map.items():
        info_data["target_view_info_list"] = target_map.get(info_id, [])
        result.append(LinkJumpInfoDTO(**info_data))
    return result


@final
class LinkJumpService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = LinkJumpRepository(session)
        self.field_repo = LinkJumpFieldRepository(session)

    async def get_table_field_with_view_id(
        self, view_id: int
    ) -> list[DatasetTableFieldDTO]:
        rows = await self.field_repo.query_table_field_with_view_id(view_id)
        return [DatasetTableFieldDTO(**row) for row in rows]

    async def query_with_view_id(
        self,
        dv_id: int,
        view_id: int,
        uid: int,
        resource_table: str = "core",
    ) -> VisualizationLinkJumpDTO | None:
        table = _table_name(resource_table)
        jump_row = await self.repo.query_jump_detail_with_view_id(
            dv_id, view_id, uid, table
        )
        if jump_row is None:
            return None

        jump_id = jump_row.get("id")
        info_rows: list[dict] = []
        if jump_id is not None:
            info_rows = await self.repo.query_link_jump_info_with_fields(
                jump_id, view_id, uid, table
            )

        info_dtos = _build_info_from_rows(info_rows)

        return VisualizationLinkJumpDTO(
            id=jump_row.get("id"),
            source_dv_id=jump_row.get("source_dv_id"),
            source_view_id=jump_row.get("source_view_id"),
            link_jump_info=jump_row.get("link_jump_info"),
            checked=jump_row.get("checked"),
            link_jump_info_array=info_dtos,
        )

    async def query_visualization_jump_info(
        self,
        dv_id: int,
        uid: int,
        resource_table: str = "core",
    ) -> LinkJumpBaseResponse:
        table = _table_name(resource_table)
        jump_rows = await self.repo.query_jumps_with_active_flag(dv_id, table)

        base_jump_info_map: dict[str, LinkJumpInfoDTO] = {}

        for jump_row in jump_rows:
            if not jump_row.get("checked"):
                continue
            source_view_id = jump_row.get("source_view_id")
            jump_id = jump_row.get("id")
            if jump_id is None:
                continue

            info_rows = await self.repo.query_link_jump_info_with_fields(
                jump_id, source_view_id, uid, table
            )
            info_dtos = _build_info_from_rows(info_rows)

            for info_dto in info_dtos:
                if not info_dto.checked:
                    continue
                source_jump_info = f"{source_view_id}#{info_dto.source_field_id}"
                if info_dto.link_type == "inner":
                    if info_dto.target_dv_id is not None:
                        base_jump_info_map[source_jump_info] = info_dto
                else:
                    base_jump_info_map[source_jump_info] = info_dto

        return LinkJumpBaseResponse(
            base_jump_info_map=base_jump_info_map,
            base_jump_info_visualization_map=None,
        )

    async def update_jump_set(self, jump_dto: VisualizationLinkJumpDTO) -> None:
        dv_id = jump_dto.source_dv_id
        view_id = jump_dto.source_view_id
        if dv_id is None or view_id is None:
            msg = "sourceDvId and sourceViewId are required"
            raise ValueError(msg)

        # Delete existing data (snapshot tables as Java does)
        await self.repo.delete_jump_target_view_info(dv_id, view_id, "snapshot")
        await self.repo.delete_jump_info(dv_id, view_id, "snapshot")
        await self.repo.delete_jump(dv_id, view_id, "snapshot")

        # Insert new data
        link_jump_id = time.time_ns()
        await self.repo.create_jump({
            "id": link_jump_id,
            "source_dv_id": dv_id,
            "source_view_id": view_id,
            "link_jump_info": jump_dto.link_jump_info,
            "checked": jump_dto.checked,
            "copy_from": jump_dto.copy_from,
            "copy_id": jump_dto.copy_id,
        })

        info_array = jump_dto.link_jump_info_array or []
        for info_dto in info_array:
            info_id = time.time_ns()
            await self.repo.create_jump_info({
                "id": info_id,
                "link_jump_id": link_jump_id,
                "link_type": info_dto.link_type,
                "jump_type": info_dto.jump_type,
                "window_size": info_dto.window_size,
                "target_dv_id": info_dto.target_dv_id,
                "source_field_id": info_dto.source_field_id,
                "content": info_dto.content,
                "checked": info_dto.checked,
                "attach_params": info_dto.attach_params,
                "copy_from": info_dto.copy_from,
                "copy_id": info_dto.copy_id,
            })

            target_list = info_dto.target_view_info_list or []
            for target_dto in target_list:
                target_id = time.time_ns()
                await self.repo.create_target_view_info({
                    "target_id": target_id,
                    "link_jump_info_id": info_id,
                    "source_field_active_id": target_dto.source_field_active_id,
                    "target_view_id": target_dto.target_view_id,
                    "target_field_id": target_dto.target_field_id,
                    "copy_from": target_dto.copy_from,
                    "copy_id": target_dto.copy_id,
                    "target_type": target_dto.target_type,
                })

        await self.session.commit()

    async def query_target_visualization_jump_info(
        self, request: LinkJumpBaseRequest
    ) -> LinkJumpBaseResponse:
        table = _table_name(request.resource_table)
        source_dv_id = request.source_dv_id
        source_view_id = request.source_view_id
        target_dv_id = request.target_dv_id
        source_field_id = request.source_field_id

        if not all([source_dv_id, source_view_id, target_dv_id]):
            return LinkJumpBaseResponse(
                base_jump_info_map=None,
                base_jump_info_visualization_map={},
            )

        rows = await self.repo.get_target_jump_info(
            source_dv_id,  # type: ignore[arg-type]
            source_view_id,  # type: ignore[arg-type]
            target_dv_id,  # type: ignore[arg-type]
            source_field_id,
            table,
        )

        viz_map: dict[str, list[str]] = {}
        for row in rows:
            source_info = row.get("sourceInfo")
            target_info = row.get("targetInfo")
            if source_info and target_info:
                viz_map.setdefault(source_info, []).append(target_info)

        return LinkJumpBaseResponse(
            base_jump_info_map=None,
            base_jump_info_visualization_map=viz_map,
        )

    async def view_table_detail_list(
        self, dv_id: int
    ) -> VisualizationComponentDTO:
        # Get visualization info
        dv_info = await self.session.get(DataVisualizationInfo, dv_id)

        if dv_info is not None:
            view_rows = await self.repo.get_view_table_details(dv_id)
            out_params = await self.repo.query_out_params_target_with_dv_id(dv_id)
            component_data = dv_info.component_data or "[]"

            # Filter views whose ID appears in component_data
            result = self._build_view_table_details(view_rows, component_data)
            out_params_dtos = [OutParamsJumpDTO(**p) for p in out_params]
        else:
            result = []
            out_params_dtos = []
            component_data = "[]"

        return VisualizationComponentDTO(
            component_data=str(component_data),
            result=result,
            out_params_jump_info=out_params_dtos,
        )

    def _build_view_table_details(
        self, rows: list[dict], component_data: str
    ) -> list[ViewTableDetailDTO]:
        """Group raw SQL rows by view ID into ViewTableDetailDTO objects."""
        view_map: dict[int, dict] = {}
        for row in rows:
            view_id = row["id"]
            if view_id not in view_map:
                view_map[view_id] = {
                    "id": view_id,
                    "title": row["title"],
                    "type": row["type"],
                    "dv_id": row["dv_id"],
                    "table_fields": [],
                }
            if row.get("field_id") is not None:
                view_map[view_id]["table_fields"].append(
                    ViewTableFieldDTO(
                        id=row["field_id"],
                        origin_name=row.get("origin_name"),
                        name=row.get("field_name"),
                        type=row.get("field_type"),
                        de_type=row.get("de_type"),
                    )
                )
        return [ViewTableDetailDTO(**v) for v in view_map.values()]

    async def update_jump_set_active(
        self,
        request: LinkJumpBaseRequest,
        uid: int,
    ) -> LinkJumpBaseResponse:
        """Toggle jump active status on a chart view, then return updated jump info."""
        # Update the chart view's jump_active flag via raw SQL
        from sqlalchemy import text

        await self.session.execute(
            text("""
                UPDATE snapshot_core_chart_view
                SET jump_active = :active
                WHERE id = :view_id
            """),
            {"active": request.active_status, "view_id": request.source_view_id},
        )
        await self.session.commit()

        # Return updated jump info
        return await self.query_visualization_jump_info(
            request.source_dv_id,  # type: ignore[arg-type]
            uid,
            "snapshot",
        )

    async def remove_jump_set(self, jump_dto: VisualizationLinkJumpDTO) -> None:
        dv_id = jump_dto.source_dv_id
        view_id = jump_dto.source_view_id
        if dv_id is None or view_id is None:
            return

        await self.repo.delete_jump_target_view_info(dv_id, view_id, "snapshot")
        await self.repo.delete_jump_info(dv_id, view_id, "snapshot")
        await self.repo.delete_jump(dv_id, view_id, "snapshot")
        await self.session.commit()


async def get_link_jump_service(
    session: AsyncSession = Depends(get_db),
) -> LinkJumpService:
    return LinkJumpService(session)
