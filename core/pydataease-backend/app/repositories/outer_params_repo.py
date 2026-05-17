from __future__ import annotations

from typing import final

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outer_params import (
    SnapshotVisualizationOuterParams,
    SnapshotVisualizationOuterParamsInfo,
    SnapshotVisualizationOuterParamsTargetViewInfo,
)


@final
class OuterParamsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Query helpers ---

    async def query_with_visualization_id(
        self, visualization_id: str
    ) -> dict | None:
        """Query top-level outer params for a visualization from snapshot tables.

        Mirrors queryWithVisualizationIdSnapshot MyBatis query.
        """
        vid = int(visualization_id)
        sql = text("""
            SELECT
                dvi.id AS visualization_id,
                COALESCE(vop.checked, false) AS checked
            FROM snapshot_data_visualization_info dvi
            LEFT JOIN snapshot_visualization_outer_params vop ON dvi.id = vop.visualization_id::bigint
            WHERE dvi.id = :visualization_id
        """)
        result = await self.session.execute(
            sql, {"visualization_id": vid}
        )
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

    async def query_outer_params_info_snapshot(
        self, visualization_id: str
    ) -> list[dict]:
        """Query param info rows with target view info from snapshot tables.

        Mirrors getOuterParamsInfoSnapshot MyBatis query.
        """
        sql = text("""
            SELECT
                pop.visualization_id,
                popi.params_info_id,
                popi.param_name,
                popi.enabled_default,
                popi.required,
                popi.default_value,
                COALESCE(popi.checked, false) AS checked,
                poptvi.target_view_id,
                poptvi.target_ds_id,
                poptvi.match_mode,
                poptvi.target_field_id
            FROM snapshot_visualization_outer_params pop
            LEFT JOIN snapshot_visualization_outer_params_info popi ON pop.params_id = popi.params_id
            LEFT JOIN snapshot_visualization_outer_params_target_view_info poptvi ON popi.params_info_id = poptvi.params_info_id
            WHERE pop.visualization_id = :visualization_id
            ORDER BY COALESCE(popi.checked, false) DESC
        """)
        result = await self.session.execute(
            sql, {"visualization_id": visualization_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_outer_params_info(
        self, visualization_id: str
    ) -> list[dict]:
        """Query outer params info mapping from live tables (checked only).

        Mirrors getVisualizationOuterParamsInfo MyBatis query.
        """
        sql = text("""
            SELECT DISTINCT
                popi.param_name AS "sourceInfo",
                popi.required,
                popi.default_value,
                popi.enabled_default,
                CONCAT(poptvi.target_view_id, '#', poptvi.target_field_id, '#', poptvi.match_mode) AS "targetInfo"
            FROM visualization_outer_params pop
            LEFT JOIN visualization_outer_params_info popi ON pop.params_id = popi.params_id
            LEFT JOIN visualization_outer_params_target_view_info poptvi ON popi.params_info_id = poptvi.params_info_id
            WHERE pop.visualization_id = :visualization_id
              AND pop.checked = true
              AND popi.checked = true
        """)
        result = await self.session.execute(
            sql, {"visualization_id": visualization_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_outer_params_info_base(
        self, visualization_id: str
    ) -> list[dict]:
        """Get existing param name -> params_info_id mapping from snapshot tables.

        Used by updateOuterParamsSet to preserve IDs by param name.
        """
        sql = text("""
            SELECT
                vopi.param_name,
                vopi.params_info_id
            FROM snapshot_visualization_outer_params_info vopi
            INNER JOIN snapshot_visualization_outer_params vop ON vop.params_id = vopi.params_id
            WHERE vop.visualization_id = :visualization_id
        """)
        result = await self.session.execute(
            sql, {"visualization_id": visualization_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def query_ds_with_visualization_id(
        self, visualization_id: str
    ) -> list[dict]:
        """Query datasets associated with a visualization's outer params.

        Mirrors queryDsWithVisualizationId MyBatis query.
        """
        vid = int(visualization_id)
        sql = text("""
            SELECT DISTINCT
                cdg.id,
                cdg.name,
                cdg.pid,
                cdg.level,
                cdg.node_type,
                cdg.type,
                cdg.mode,
                cdg.info,
                cdg.create_by,
                cdg.create_time,
                cdg.qrtz_instance,
                cdg.sync_status,
                cdg.update_by,
                cdg.last_update_time,
                dvi.id AS "visualizationId"
            FROM core_dataset_group cdg
            INNER JOIN snapshot_core_chart_view ccv ON cdg.id = ccv.table_id
                AND ccv.type != 'VQuery'
            INNER JOIN snapshot_data_visualization_info dvi ON ccv.scene_id = dvi.id
            WHERE ccv.scene_id = :visualization_id
              AND dvi.id = :visualization_id
              AND POSITION(CAST(ccv.id AS TEXT) IN dvi.component_data) > 0
        """)
        result = await self.session.execute(
            sql, {"visualization_id": vid}
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def query_ds_fields(self, dataset_group_id: int) -> list[dict]:
        """Query dataset fields for a dataset group."""
        sql = text("""
            SELECT cdtf.*, cdtf.id AS "attachId"
            FROM core_dataset_table_field cdtf
            WHERE cdtf.dataset_group_id = :dataset_group_id
            ORDER BY cdtf.de_type, cdtf.origin_name
        """)
        result = await self.session.execute(
            sql, {"dataset_group_id": dataset_group_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def query_ds_views(
        self, dataset_group_id: int, visualization_id: str
    ) -> list[dict]:
        """Query chart views for a dataset group within a visualization."""
        vid = int(visualization_id)
        sql = text("""
            SELECT DISTINCT
                ccv.id AS "chartId",
                ccv.title AS "chartName",
                ccv.type AS "chartType"
            FROM snapshot_core_chart_view ccv
            INNER JOIN snapshot_data_visualization_info dvi ON ccv.scene_id = dvi.id
            WHERE ccv.table_id = :dataset_group_id
              AND ccv.type != 'VQuery'
              AND dvi.id = :visualization_id
              AND POSITION(CAST(ccv.id AS TEXT) IN dvi.component_data) > 0
        """)
        result = await self.session.execute(
            sql,
            {"dataset_group_id": dataset_group_id, "visualization_id": vid},
        )
        return [dict(row._mapping) for row in result.fetchall()]

    # --- Delete helpers (snapshot tables) ---

    async def delete_target_view_info_snapshot(
        self, visualization_id: str
    ) -> None:
        sql = text("""
            DELETE FROM snapshot_visualization_outer_params_target_view_info poptvi
            WHERE poptvi.params_info_id IN (
                SELECT params_info_id FROM (
                    SELECT poptvi.params_info_id
                    FROM snapshot_visualization_outer_params_target_view_info poptvi
                    INNER JOIN snapshot_visualization_outer_params_info popi ON poptvi.params_info_id = popi.params_info_id
                    INNER JOIN snapshot_visualization_outer_params pop ON popi.params_id = pop.params_id
                    WHERE pop.visualization_id = :visualization_id
                ) tmp
            )
        """)
        await self.session.execute(sql, {"visualization_id": visualization_id})

    async def delete_params_info_snapshot(
        self, visualization_id: str
    ) -> None:
        sql = text("""
            DELETE FROM snapshot_visualization_outer_params_info popi
            WHERE popi.params_id IN (
                SELECT params_id FROM (
                    SELECT popi.params_id
                    FROM snapshot_visualization_outer_params_info popi
                    INNER JOIN snapshot_visualization_outer_params pop ON popi.params_id = pop.params_id
                    WHERE pop.visualization_id = :visualization_id
                ) tmp
            )
        """)
        await self.session.execute(sql, {"visualization_id": visualization_id})

    async def delete_outer_params_snapshot(
        self, visualization_id: str
    ) -> None:
        sql = text("""
            DELETE FROM snapshot_visualization_outer_params pop
            WHERE pop.visualization_id = :visualization_id
        """)
        await self.session.execute(sql, {"visualization_id": visualization_id})

    # --- Insert helpers (snapshot tables) ---

    async def insert_outer_params_snapshot(
        self, payload: dict[str, object]
    ) -> SnapshotVisualizationOuterParams:
        entity = SnapshotVisualizationOuterParams(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def insert_params_info_snapshot(
        self, payload: dict[str, object]
    ) -> SnapshotVisualizationOuterParamsInfo:
        entity = SnapshotVisualizationOuterParamsInfo(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def insert_target_view_info_snapshot(
        self, payload: dict[str, object]
    ) -> SnapshotVisualizationOuterParamsTargetViewInfo:
        entity = SnapshotVisualizationOuterParamsTargetViewInfo(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity
