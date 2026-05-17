from __future__ import annotations

from typing import final

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.link_jump import (
    VisualizationLinkJump,
    VisualizationLinkJumpInfo,
    VisualizationLinkJumpTargetViewInfo,
)


@final
class LinkJumpRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Basic CRUD ---

    async def get_jump_by_id(self, jump_id: int) -> VisualizationLinkJump | None:
        return await self.session.get(VisualizationLinkJump, jump_id)

    async def get_jump_info_by_id(self, info_id: int) -> VisualizationLinkJumpInfo | None:
        return await self.session.get(VisualizationLinkJumpInfo, info_id)

    async def create_jump(self, payload: dict[str, object]) -> VisualizationLinkJump:
        entity = VisualizationLinkJump(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def create_jump_info(self, payload: dict[str, object]) -> VisualizationLinkJumpInfo:
        entity = VisualizationLinkJumpInfo(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def create_target_view_info(
        self, payload: dict[str, object]
    ) -> VisualizationLinkJumpTargetViewInfo:
        entity = VisualizationLinkJumpTargetViewInfo(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity

    # --- Query helpers ---

    async def query_jumps_by_dv_id(self, dv_id: int) -> list[VisualizationLinkJump]:
        result = await self.session.execute(
            select(VisualizationLinkJump).where(
                VisualizationLinkJump.source_dv_id == dv_id
            )
        )
        return list(result.scalars().all())

    async def query_jump_by_dv_and_view(
        self, dv_id: int, view_id: int
    ) -> VisualizationLinkJump | None:
        result = await self.session.execute(
            select(VisualizationLinkJump).where(
                VisualizationLinkJump.source_dv_id == dv_id,
                VisualizationLinkJump.source_view_id == view_id,
            )
        )
        return result.scalar_one_or_none()

    async def query_jump_infos_by_jump_id(
        self, jump_id: int
    ) -> list[VisualizationLinkJumpInfo]:
        result = await self.session.execute(
            select(VisualizationLinkJumpInfo).where(
                VisualizationLinkJumpInfo.link_jump_id == jump_id
            )
        )
        return list(result.scalars().all())

    async def query_target_view_infos_by_info_id(
        self, info_id: int
    ) -> list[VisualizationLinkJumpTargetViewInfo]:
        result = await self.session.execute(
            select(VisualizationLinkJumpTargetViewInfo).where(
                VisualizationLinkJumpTargetViewInfo.link_jump_info_id == info_id
            )
        )
        return list(result.scalars().all())

    async def query_jumps_with_active_flag(
        self, dv_id: int, table_name: str
    ) -> list[dict[str, object]]:
        """Query jumps joined with chart view's jump_active flag.

        Returns rows matching the Java queryWithDvId SQL:
        for core tables or snapshot tables based on table_name.
        """
        if "snapshot" in table_name:
            cv = "snapshot_core_chart_view"
        else:
            cv = "core_chart_view"

        if "snapshot" in table_name:
            jtable = "snapshot_visualization_link_jump"
        else:
            jtable = "visualization_link_jump"

        sql = text(f"""
            SELECT ccv.id AS source_view_id,
                   vlj.id,
                   CAST(:dv_id AS bigint) AS source_dv_id,
                   vlj.link_jump_info,
                   COALESCE(ccv.jump_active, false) AS checked
            FROM {cv} ccv
            LEFT JOIN {jtable} vlj ON ccv.id = vlj.source_view_id
            WHERE vlj.source_dv_id = :dv_id
              AND ccv.jump_active = true
        """)
        result = await self.session.execute(sql, {"dv_id": dv_id})
        return [dict(row._mapping) for row in result.fetchall()]

    async def query_jump_detail_with_view_id(
        self,
        dv_id: int,
        view_id: int,
        uid: int,
        table_name: str = "snapshot",
    ) -> dict[str, object] | None:
        """Query jump config for a specific view (queryWithViewId).

        Returns the jump row plus nested info.
        """
        if "snapshot" in table_name:
            jtable = "snapshot_visualization_link_jump"
            cv = "snapshot_core_chart_view"
        else:
            jtable = "visualization_link_jump"
            cv = "core_chart_view"

        sql = text(f"""
            SELECT ccv.id AS source_view_id,
                   vlj.id,
                   CAST(:dv_id AS bigint) AS source_dv_id,
                   vlj.link_jump_info,
                   COALESCE(vlj.checked, false) AS checked
            FROM {cv} ccv
            LEFT JOIN {jtable} vlj ON ccv.id = vlj.source_view_id
                AND vlj.source_dv_id = :dv_id
            WHERE ccv.id = :view_id
        """)
        result = await self.session.execute(
            sql, {"dv_id": dv_id, "view_id": view_id}
        )
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

    async def query_link_jump_info_with_fields(
        self,
        jump_id: int,
        source_view_id: int,
        uid: int,
        table_name: str = "snapshot",
    ) -> list[dict[str, object]]:
        """Query jump info rows with field details (getLinkJumpInfo).

        This mirrors the complex Java MyBatis query that joins chart views,
        dataset fields, jump info, target view info, and xpack shares.
        """
        if "snapshot" in table_name:
            cv = "snapshot_core_chart_view"
            jtable = "snapshot_visualization_link_jump"
            jitable = "snapshot_visualization_link_jump_info"
            tvitable = "snapshot_visualization_link_jump_target_view_info"
            optable = "snapshot_visualization_outer_params_info"
        else:
            cv = "core_chart_view"
            jtable = "visualization_link_jump"
            jitable = "visualization_link_jump_info"
            tvitable = "visualization_link_jump_target_view_info"
            optable = "visualization_outer_params_info"

        sql = text(f"""
            SELECT
                cdtf.id AS source_field_id,
                cdtf.de_type AS source_de_type,
                cdtf.name AS source_field_name,
                vlji.id,
                vlji.link_jump_id,
                vlji.link_type,
                vlji.jump_type,
                vlji.window_size,
                vlji.target_dv_id,
                dvi.type AS target_dv_type,
                vlji.content,
                COALESCE(vlji.checked, false) AS checked,
                COALESCE(vlji.attach_params, false) AS attach_params,
                vljtvi.target_id,
                vljtvi.target_view_id,
                vljtvi.target_field_id,
                vljtvi.target_type,
                vljtvi.source_field_active_id,
                vopi.param_name AS outer_params_name
            FROM {cv} ccv
            LEFT JOIN core_dataset_table_field cdtf
                ON ccv.table_id = cdtf.dataset_group_id
            LEFT JOIN {jtable} vlj ON ccv.id = vlj.source_view_id
                AND vlj.id = :jump_id
            LEFT JOIN {jitable} vlji ON vlj.id = vlji.link_jump_id
                AND cdtf.id = vlji.source_field_id
            LEFT JOIN data_visualization_info dvi ON vlji.target_dv_id = dvi.id
            LEFT JOIN {tvitable} vljtvi ON vlji.id = vljtvi.link_jump_info_id
            LEFT JOIN {optable} vopi ON vopi.params_info_id = vljtvi.target_view_id
            WHERE ccv.id = :source_view_id
              AND ccv.type != 'VQuery'
            ORDER BY cdtf.name
        """)
        result = await self.session.execute(
            sql, {"jump_id": jump_id, "source_view_id": source_view_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_target_jump_info(
        self,
        source_dv_id: int,
        source_view_id: int,
        target_dv_id: int,
        source_field_id: int | None = None,
        table_name: str = "core",
    ) -> list[dict[str, object]]:
        """Query target visualization jump info (getTargetVisualizationJumpInfo)."""
        if "snapshot" in table_name:
            jtable = "snapshot_visualization_link_jump"
            jitable = "snapshot_visualization_link_jump_info"
            tvitable = "snapshot_visualization_link_jump_target_view_info"
        else:
            jtable = "visualization_link_jump"
            jitable = "visualization_link_jump_info"
            tvitable = "visualization_link_jump_target_view_info"

        sql = text(f"""
            SELECT DISTINCT
                CONCAT(lj.source_view_id, '#', jtvi.source_field_active_id, '#', lji.source_field_id) AS "sourceInfo",
                CONCAT(jtvi.target_view_id, '#', jtvi.target_field_id) AS "targetInfo"
            FROM {tvitable} jtvi
            LEFT JOIN {jitable} lji ON jtvi.link_jump_info_id = lji.id
            LEFT JOIN {jtable} lj ON lji.link_jump_id = lj.id
            WHERE lji.checked = true
              AND lj.source_dv_id = :source_dv_id
              AND lj.source_view_id = :source_view_id
              AND lji.target_dv_id = :target_dv_id
        """)
        params: dict[str, object] = {
            "source_dv_id": source_dv_id,
            "source_view_id": source_view_id,
            "target_dv_id": target_dv_id,
        }
        if source_field_id is not None:
            sql = text(sql.text + " AND lji.source_field_id = :source_field_id")
            params["source_field_id"] = source_field_id

        result = await self.session.execute(sql, params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_view_table_details(self, dv_id: int) -> list[dict[str, object]]:
        """Get view table field details for a dashboard (getViewTableDetails)."""
        sql = text("""
            SELECT
                core_chart_view.id,
                core_chart_view.title,
                core_chart_view.type,
                core_chart_view.scene_id AS dv_id,
                core_dataset_table_field.id AS field_id,
                core_dataset_table_field.origin_name,
                core_dataset_table_field.name AS field_name,
                core_dataset_table_field.type AS field_type,
                core_dataset_table_field.de_type
            FROM core_chart_view
            LEFT JOIN core_dataset_table_field
                ON core_chart_view.table_id = core_dataset_table_field.dataset_group_id
            INNER JOIN data_visualization_info dvi
                ON core_chart_view.scene_id = dvi.id
            WHERE core_chart_view.scene_id = :dv_id
              AND core_chart_view.type != 'VQuery'
              AND core_chart_view.table_id IS NOT NULL
              AND dvi.id = :dv_id
              AND POSITION(CAST(core_chart_view.id AS TEXT) IN dvi.component_data) > 0
        """)
        result = await self.session.execute(sql, {"dv_id": dv_id})
        return [dict(row._mapping) for row in result.fetchall()]

    async def query_out_params_target_with_dv_id(self, dv_id: int) -> list[dict[str, object]]:
        """Query outer params jump targets for a dashboard."""
        sql = text("""
            SELECT
                vopi.params_info_id AS id,
                vopi.param_name AS name,
                vopi.param_name AS title,
                'outerParams' AS type
            FROM visualization_outer_params_info vopi
            LEFT JOIN visualization_outer_params vop ON vopi.params_id = vop.params_id
            WHERE vop.visualization_id = :dv_id
        """)
        result = await self.session.execute(sql, {"dv_id": dv_id})
        return [dict(row._mapping) for row in result.fetchall()]

    # --- Delete helpers ---

    async def delete_jump_target_view_info(
        self, dv_id: int, view_id: int, table_name: str = "snapshot"
    ) -> None:
        if "snapshot" in table_name:
            tvitable = "snapshot_visualization_link_jump_target_view_info"
            jitable = "snapshot_visualization_link_jump_info"
            jtable = "snapshot_visualization_link_jump"
        else:
            tvitable = "visualization_link_jump_target_view_info"
            jitable = "visualization_link_jump_info"
            jtable = "visualization_link_jump"

        sql = text(f"""
            DELETE FROM {tvitable}
            WHERE link_jump_info_id IN (
                SELECT lji.id
                FROM {jitable} lji
                JOIN {jtable} lj ON lji.link_jump_id = lj.id
                WHERE lj.source_dv_id = :dv_id
                  AND lj.source_view_id = :view_id
            )
        """)
        await self.session.execute(sql, {"dv_id": dv_id, "view_id": view_id})

    async def delete_jump_info(
        self, dv_id: int, view_id: int, table_name: str = "snapshot"
    ) -> None:
        if "snapshot" in table_name:
            jitable = "snapshot_visualization_link_jump_info"
            jtable = "snapshot_visualization_link_jump"
        else:
            jitable = "visualization_link_jump_info"
            jtable = "visualization_link_jump"

        sql = text(f"""
            DELETE FROM {jitable}
            WHERE link_jump_id IN (
                SELECT lj.id
                FROM {jtable} lj
                WHERE lj.source_dv_id = :dv_id
                  AND lj.source_view_id = :view_id
            )
        """)
        await self.session.execute(sql, {"dv_id": dv_id, "view_id": view_id})

    async def delete_jump(
        self, dv_id: int, view_id: int, table_name: str = "snapshot"
    ) -> None:
        if "snapshot" in table_name:
            jtable = "snapshot_visualization_link_jump"
        else:
            jtable = "visualization_link_jump"

        sql = text(f"""
            DELETE FROM {jtable}
            WHERE source_dv_id = :dv_id
              AND source_view_id = :view_id
        """)
        await self.session.execute(sql, {"dv_id": dv_id, "view_id": view_id})

    async def delete_all_for_visualization(
        self, dv_id: int, table_name: str = "core"
    ) -> None:
        """Delete all jump data for a visualization (all three tables)."""
        await self.delete_jump(dv_id, dv_id, table_name)
        # For visualization-level delete we use dv_id as a wildcard
        # But the SQL requires both params; for full cleanup we delete by dv_id only
        if "snapshot" in table_name:
            tvitable = "snapshot_visualization_link_jump_target_view_info"
            jitable = "snapshot_visualization_link_jump_info"
            jtable = "snapshot_visualization_link_jump"
        else:
            tvitable = "visualization_link_jump_target_view_info"
            jitable = "visualization_link_jump_info"
            jtable = "visualization_link_jump"

        await self.session.execute(text(f"""
            DELETE FROM {tvitable}
            WHERE link_jump_info_id IN (
                SELECT lji.id FROM {jitable} lji
                JOIN {jtable} lj ON lji.link_jump_id = lj.id
                WHERE lj.source_dv_id = :dv_id
            )
        """), {"dv_id": dv_id})
        await self.session.execute(text(f"""
            DELETE FROM {jitable}
            WHERE link_jump_id IN (
                SELECT lj.id FROM {jtable} lj WHERE lj.source_dv_id = :dv_id
            )
        """), {"dv_id": dv_id})
        await self.session.execute(text(f"""
            DELETE FROM {jtable} WHERE source_dv_id = :dv_id
        """), {"dv_id": dv_id})


@final
class LinkJumpFieldRepository:
    """Repository for querying dataset table fields (for getTableFieldWithViewId)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def query_table_field_with_view_id(self, view_id: int) -> list[dict[str, object]]:
        """Query table fields associated with a chart view.

        Mirrors extVisualizationLinkageMapper.queryTableFieldWithViewId.
        """
        sql = text("""
            SELECT cdtf.id, cdtf.origin_name, cdtf.name, cdtf.type, cdtf.de_type
            FROM core_dataset_table_field cdtf
            INNER JOIN core_chart_view ccv ON ccv.table_id = cdtf.dataset_group_id
            WHERE ccv.id = :view_id
              AND cdtf.checked = true
              AND cdtf.group_type = 'd'
            ORDER BY cdtf.column_index
        """)
        result = await self.session.execute(sql, {"view_id": view_id})
        return [dict(row._mapping) for row in result.fetchall()]
