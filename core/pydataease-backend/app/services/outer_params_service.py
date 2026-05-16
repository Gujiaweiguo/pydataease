from __future__ import annotations

import uuid
from collections import defaultdict
from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.outer_params_repo import OuterParamsRepository
from app.schemas.outer_params import (
    OuterParamsBaseResponse,
    OuterParamsInfoDTO,
    OuterParamsTargetViewInfoDTO,
    VisualizationOuterParamsDTO,
)


@final
class OuterParamsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OuterParamsRepository(session)

    async def query_with_visualization_id(
        self, visualization_id: str
    ) -> VisualizationOuterParamsDTO | None:
        """Query full outer params config for a visualization."""
        top_row = await self.repo.query_with_visualization_id(visualization_id)
        if top_row is None:
            return None

        info_rows = await self.repo.query_outer_params_info_snapshot(visualization_id)

        # Group info rows by params_info_id and build DTOs
        info_map: dict[str, dict] = {}
        target_map: dict[str, list[OuterParamsTargetViewInfoDTO]] = defaultdict(list)

        for row in info_rows:
            info_id = row.get("params_info_id")
            if info_id is None:
                continue
            if info_id not in info_map:
                info_map[info_id] = {
                    "params_info_id": info_id,
                    "params_id": None,
                    "param_name": row.get("param_name"),
                    "checked": row.get("checked"),
                    "required": row.get("required"),
                    "default_value": row.get("default_value"),
                    "enabled_default": row.get("enabled_default"),
                }
            target_view_id = row.get("target_view_id")
            if target_view_id is not None:
                target_map[info_id].append(
                    OuterParamsTargetViewInfoDTO(
                        target_view_id=str(target_view_id),
                        target_ds_id=str(row.get("target_ds_id", "")),
                        target_field_id=str(row.get("target_field_id", "")),
                        match_mode=row.get("match_mode"),
                    )
                )

        info_dtos: list[OuterParamsInfoDTO] = []
        for info_id, info_data in info_map.items():
            info_data["target_view_info_list"] = target_map.get(info_id, [])
            info_dtos.append(OuterParamsInfoDTO(**info_data))

        return VisualizationOuterParamsDTO(
            params_id=None,
            visualization_id=visualization_id,
            checked=top_row.get("checked", False),
            outer_params_info_array=info_dtos,
        )

    async def update_outer_params_set(
        self, dto: VisualizationOuterParamsDTO
    ) -> None:
        """Save/update outer params configuration (writes to snapshot tables)."""
        visualization_id = dto.visualization_id
        if visualization_id is None:
            msg = "visualizationId cannot be null"
            raise ValueError(msg)

        # Build existing param name -> params_info_id mapping
        existing_info = await self.repo.get_outer_params_info_base(visualization_id)
        params_info_name_id_map: dict[str, str] = {
            r["param_name"]: r["params_info_id"] for r in existing_info
        }

        # Delete existing data from snapshot tables
        await self.repo.delete_target_view_info_snapshot(visualization_id)
        await self.repo.delete_params_info_snapshot(visualization_id)
        await self.repo.delete_outer_params_snapshot(visualization_id)

        info_array = dto.outer_params_info_array or []
        if not info_array:
            await self.session.commit()
            return

        # Insert new top-level params record
        params_id = str(uuid.uuid4())
        await self.repo.insert_outer_params_snapshot({
            "params_id": params_id,
            "visualization_id": visualization_id,
            "checked": dto.checked,
            "remark": dto.remark,
            "copy_from": dto.copy_from,
            "copy_id": dto.copy_id,
        })

        # Insert param info records and their target view info
        for info_dto in info_array:
            # Preserve existing params_info_id by param name
            params_info_id = params_info_name_id_map.get(
                info_dto.param_name or "", str(uuid.uuid4())
            )

            await self.repo.insert_params_info_snapshot({
                "params_info_id": params_info_id,
                "params_id": params_id,
                "param_name": info_dto.param_name,
                "checked": info_dto.checked,
                "required": info_dto.required,
                "default_value": info_dto.default_value,
                "enabled_default": info_dto.enabled_default,
                "copy_from": info_dto.copy_from,
                "copy_id": info_dto.copy_id,
            })

            target_list = info_dto.target_view_info_list or []
            for target_dto in target_list:
                target_id = str(uuid.uuid4())
                await self.repo.insert_target_view_info_snapshot({
                    "target_id": target_id,
                    "params_info_id": params_info_id,
                    "target_view_id": target_dto.target_view_id,
                    "target_ds_id": target_dto.target_ds_id,
                    "target_field_id": target_dto.target_field_id,
                    "copy_from": target_dto.copy_from,
                    "copy_id": target_dto.copy_id,
                    "match_mode": target_dto.match_mode,
                })

        await self.session.commit()

    async def get_outer_params_info(
        self, visualization_id: str
    ) -> OuterParamsBaseResponse:
        """Get outer params info mapping (param name -> target info list)."""
        rows = await self.repo.get_outer_params_info(visualization_id)

        # Build outerParamsInfoMap: sourceInfo -> [targetInfo, ...]
        info_map: dict[str, list[str]] = defaultdict(list)
        # Build outerParamsInfoBaseMap: sourceInfo -> InfoDTO
        base_map: dict[str, OuterParamsInfoDTO] = {}

        for row in rows:
            source_info = row.get("sourceInfo")
            target_info = row.get("targetInfo")
            if source_info:
                if target_info:
                    info_map[source_info].append(target_info)
                if source_info not in base_map:
                    base_map[source_info] = OuterParamsInfoDTO(
                        source_info=source_info,
                        required=row.get("required"),
                        default_value=row.get("default_value"),
                        enabled_default=row.get("enabled_default"),
                        target_info_list=info_map.get(source_info, []),
                    )
                else:
                    # Update target_info_list reference
                    base_map[source_info].target_info_list = info_map.get(
                        source_info, []
                    )

        return OuterParamsBaseResponse(
            outer_params_info_map=dict(info_map) if info_map else None,
            outer_params_info_base_map=base_map if base_map else None,
        )

    async def query_ds_with_visualization_id(
        self, visualization_id: str
    ) -> list[dict]:
        """Query datasets associated with a visualization's outer params.

        Returns a list of dataset group dicts with nested fields and views.
        """
        ds_rows = await self.repo.query_ds_with_visualization_id(visualization_id)
        result: list[dict] = []
        for ds_row in ds_rows:
            ds_id = ds_row.get("id")
            fields = await self.repo.query_ds_fields(ds_id) if ds_id else []
            views = (
                await self.repo.query_ds_views(ds_id, visualization_id)
                if ds_id
                else []
            )
            result.append({
                **ds_row,
                "datasetFields": fields,
                "datasetViews": views,
            })
        return result


async def get_outer_params_service(
    session: AsyncSession = Depends(get_db),
) -> OuterParamsService:
    return OuterParamsService(session)
