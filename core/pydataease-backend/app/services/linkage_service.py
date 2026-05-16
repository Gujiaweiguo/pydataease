from __future__ import annotations

import time
from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.linkage_repo import LinkageRepository
from app.schemas.linkage import (
    LinkageFieldVO,
    LinkageGatherRequest,
    LinkageRemoveRequest,
    LinkageSaveRequest,
    LinkageUpdateActiveRequest,
    VisualizationLinkageDTO,
)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_id() -> int:
    return time.time_ns()


@final
class LinkageService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = LinkageRepository(session)

    async def get_view_linkage_gather(
        self, request: LinkageGatherRequest
    ) -> dict[str, VisualizationLinkageDTO]:
        """Get linkage gather as a map keyed by target_view_id (string).

        Mirrors Java getViewLinkageGather.
        """
        resource_table = "snapshot" if request.resource_table == "snapshot" else "core"
        target_ids = [int(tid) for tid in request.target_view_ids]
        rows = await self.repo.get_view_linkage_gather(
            request.dv_id, request.source_view_id, target_ids, resource_table
        )
        return self._build_linkage_gather_map(rows)

    async def get_view_linkage_gather_array(
        self, request: LinkageGatherRequest
    ) -> list[VisualizationLinkageDTO]:
        """Get linkage gather as a list.

        Mirrors Java getViewLinkageGatherArray.
        """
        resource_table = "snapshot" if request.resource_table == "snapshot" else "core"
        target_ids = [int(tid) for tid in request.target_view_ids]
        rows = await self.repo.get_view_linkage_gather(
            request.dv_id, request.source_view_id, target_ids, resource_table
        )
        return self._build_linkage_gather_list(rows)

    async def save_linkage(self, request: LinkageSaveRequest) -> None:
        """Save linkage configuration.

        Mirrors Java saveLinkage — deletes existing linkage for source, then recreates.
        Always writes to snapshot tables (as Java does).
        """
        dv_id = request.dv_id
        source_view_id = request.source_view_id
        update_time = _timestamp_ms()

        # Delete existing data (snapshot tables)
        await self.repo.delete_view_linkage_field(dv_id, source_view_id, "snapshot")
        await self.repo.delete_view_linkage(dv_id, source_view_id, "snapshot")

        # Recreate linkage from request
        for linkage_dto in request.linkage_info:
            target_view_id = linkage_dto.target_view_id
            if target_view_id is None or target_view_id == source_view_id:
                continue

            linkage_id = _new_id()
            await self.repo.create_linkage({
                "id": linkage_id,
                "dv_id": dv_id,
                "source_view_id": source_view_id,
                "target_view_id": target_view_id,
                "update_time": update_time,
                "update_people": "",
                "linkage_active": linkage_dto.linkage_active or False,
                "ext1": None,
                "ext2": None,
                "copy_from": None,
                "copy_id": None,
            }, "snapshot")

            if linkage_dto.linkage_active and linkage_dto.linkage_fields:
                for field_vo in linkage_dto.linkage_fields:
                    field_id = _new_id()
                    await self.repo.create_linkage_field({
                        "id": field_id,
                        "linkage_id": linkage_id,
                        "source_field": field_vo.source_field,
                        "target_field": field_vo.target_field,
                        "update_time": update_time,
                        "copy_from": field_vo.copy_from,
                        "copy_id": field_vo.copy_id,
                    }, "snapshot")

        await self.session.commit()

    async def get_visualization_all_linkage_info(
        self, dv_id: int, resource_table: str
    ) -> dict[str, list[str]]:
        """Get all linkage info for a visualization.

        Mirrors Java getVisualizationAllLinkageInfo.
        Returns map of sourceInfo -> list of targetInfo strings.
        """
        table = "snapshot" if resource_table == "snapshot" else "core"
        rows = await self.repo.get_panel_all_linkage_info(dv_id, table)

        result: dict[str, list[str]] = {}
        for row in rows:
            source_info = row.get("sourceInfo")
            target_info = row.get("targetInfo")
            if source_info and target_info:
                result.setdefault(source_info, []).append(target_info)
        return result

    async def update_linkage_active(
        self, request: LinkageUpdateActiveRequest
    ) -> dict[str, list[str]]:
        """Toggle linkage active on a chart view.

        Mirrors Java updateLinkageActive — updates snapshot_core_chart_view,
        then returns getVisualizationAllLinkageInfo.
        """
        await self.repo.update_chart_linkage_active(
            request.source_view_id, request.active_status
        )
        await self.session.commit()
        return await self.get_visualization_all_linkage_info(request.dv_id, "snapshot")

    async def remove_linkage(self, request: LinkageRemoveRequest) -> None:
        """Remove linkage for a source view.

        Mirrors Java removeLinkage — deletes from snapshot tables.
        """
        await self.repo.delete_view_linkage_field(
            request.dv_id, request.source_view_id, "snapshot"
        )
        await self.repo.delete_view_linkage(
            request.dv_id, request.source_view_id, "snapshot"
        )
        await self.session.commit()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_linkage_gather_map(
        rows: list[dict],
    ) -> dict[str, VisualizationLinkageDTO]:
        """Group flat SQL rows into a map keyed by target_view_id string."""
        grouped = LinkageService._group_rows_by_target(rows)
        return {
            str(target_id): dto for target_id, dto in grouped.items()
        }

    @staticmethod
    def _build_linkage_gather_list(
        rows: list[dict],
    ) -> list[VisualizationLinkageDTO]:
        """Group flat SQL rows into a list of VisualizationLinkageDTO."""
        grouped = LinkageService._group_rows_by_target(rows)
        return list(grouped.values())

    @staticmethod
    def _group_rows_by_target(
        rows: list[dict],
    ) -> dict[int, VisualizationLinkageDTO]:
        """Group flat SQL rows by target_view_id into VisualizationLinkageDTO objects.

        Each row may have one linkage field (source_field, target_field).
        Rows with same target_view_id get grouped together with multiple linkage fields.
        """
        result: dict[int, VisualizationLinkageDTO] = {}

        for row in rows:
            target_id = row.get("target_view_id")
            if target_id is None:
                continue

            if target_id not in result:
                result[target_id] = VisualizationLinkageDTO(
                    target_view_id=target_id,
                    target_view_name=row.get("targetViewName"),
                    target_view_type=row.get("target_view_type"),
                    source_view_id=row.get("sourceViewId"),
                    linkage_active=row.get("linkageActive") or False,
                    table_id=row.get("table_id"),
                    linkage_fields=[],
                    target_view_fields=[],
                )

            dto = result[target_id]

            # Add linkage field if present
            source_field = row.get("source_field")
            target_field = row.get("target_field")
            if source_field is not None or target_field is not None:
                dto.linkage_fields.append(LinkageFieldVO(
                    source_field=source_field,
                    target_field=target_field,
                ))

        return result


async def get_linkage_service(
    session: AsyncSession = Depends(get_db),
) -> LinkageService:
    return LinkageService(session)
