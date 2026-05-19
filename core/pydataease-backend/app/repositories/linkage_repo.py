from __future__ import annotations

from typing import final

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _table_names(resource_table: str) -> tuple[str, str, str]:
    """Return (linkage_table, linkage_field_table, chart_view_table) based on resource_table."""
    if resource_table == "snapshot":
        return (
            "snapshot_visualization_linkage",
            "snapshot_visualization_linkage_field",
            "snapshot_core_chart_view",
        )
    return (
        "visualization_linkage",
        "visualization_linkage_field",
        "core_chart_view",
    )


@final
class LinkageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    async def get_view_linkage_gather(
        self,
        dv_id: int,
        source_view_id: int,
        target_view_ids: list[int],
        resource_table: str = "core",
    ) -> list[dict]:
        """Query linkage gather data for a source view against target views.

        Mirrors ExtVisualizationLinkageMapper.getViewLinkageGather.
        Returns flat rows that need to be grouped by target_view_id.
        """
        lt, lft, cv = _table_names(resource_table)

        if not target_view_ids:
            return []

        placeholders = ", ".join(f":tid_{i}" for i in range(len(target_view_ids)))
        params: dict[str, object] = {
            "dv_id": dv_id,
            "source_view_id": source_view_id,
        }
        for i, tid in enumerate(target_view_ids):
            params[f"tid_{i}"] = tid

        sql = text(f"""
            SELECT
                ccv.title AS "targetViewName",
                ccv.id AS target_view_id,
                ccv.type AS target_view_type,
                ccv.table_id,
                vl.source_view_id AS "sourceViewId",
                (CASE WHEN vl.target_view_id IS NULL THEN false ELSE vl.linkage_active END) AS "linkageActive",
                vlf.source_field,
                vlf.target_field
            FROM {cv} ccv
            LEFT JOIN {lt} vl
                ON ccv.id = vl.target_view_id
                AND vl.dv_id = :dv_id
                AND vl.source_view_id = :source_view_id
            LEFT JOIN {lft} vlf
                ON vl.id = vlf.linkage_id
            WHERE ccv.type != 'VQuery'
              AND ccv.id IN ({placeholders})
        """)
        result = await self.session.execute(sql, params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_panel_all_linkage_info(
        self,
        dv_id: int,
        resource_table: str = "core",
    ) -> list[dict]:
        """Get all linkage info for a visualization.

        Mirrors ExtVisualizationLinkageMapper.getPanelAllLinkageInfo(Snapshot).
        Returns rows with sourceInfo and targetInfo columns.
        """
        lt, lft, cv = _table_names(resource_table)

        sql = text(f"""
            SELECT DISTINCT
                CONCAT(vl.source_view_id, '#', vlf.source_field) AS "sourceInfo",
                CONCAT(vl.target_view_id, '#', vlf.target_field) AS "targetInfo"
            FROM {lt} vl
            LEFT JOIN {cv} ccv ON vl.source_view_id = ccv.id
            LEFT JOIN {lft} vlf ON vl.id = vlf.linkage_id
            WHERE vl.dv_id = :dv_id
              AND ccv.linkage_active = true
              AND vl.linkage_active = true
              AND vlf.id IS NOT NULL
        """)
        result = await self.session.execute(sql, {"dv_id": dv_id})
        return [dict(row._mapping) for row in result.fetchall()]

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    async def delete_view_linkage_field(
        self,
        dv_id: int,
        source_view_id: int | None = None,
        resource_table: str = "snapshot",
    ) -> None:
        """Delete linkage fields for a dv/source pair.

        Mirrors deleteViewLinkageField(Snapshot).
        """
        _, lft, _ = _table_names(resource_table)
        lt, _, _ = _table_names(resource_table)

        extra = " AND pvl.source_view_id = :source_view_id" if source_view_id is not None else ""
        params: dict[str, object] = {"dv_id": dv_id}
        if source_view_id is not None:
            params["source_view_id"] = source_view_id

        sql = text(f"""
            DELETE FROM {lft}
            WHERE linkage_id IN (
                SELECT id FROM (
                    SELECT pvl.id
                    FROM {lt} pvl
                    WHERE pvl.dv_id = :dv_id{extra}
                ) AS temp_table
            )
        """)
        await self.session.execute(sql, params)

    async def delete_view_linkage(
        self,
        dv_id: int,
        source_view_id: int | None = None,
        resource_table: str = "snapshot",
    ) -> None:
        """Delete linkage records for a dv/source pair.

        Mirrors deleteViewLinkage(Snapshot).
        """
        lt, _, _ = _table_names(resource_table)

        extra = " AND source_view_id = :source_view_id" if source_view_id is not None else ""
        params: dict[str, object] = {"dv_id": dv_id}
        if source_view_id is not None:
            params["source_view_id"] = source_view_id

        sql = text(f"""
            DELETE FROM {lt}
            WHERE dv_id = :dv_id{extra}
        """)
        await self.session.execute(sql, params)

    _LINKAGE_COLUMNS = {
        "id", "dv_id", "source_view_id", "target_view_id",
        "update_time", "update_people", "linkage_active",
        "ext1", "ext2", "copy_from", "copy_id",
    }

    _LINKAGE_FIELD_COLUMNS = {
        "id", "linkage_id", "source_field", "target_field",
        "update_time", "copy_from", "copy_id",
    }

    async def create_linkage(
        self,
        payload: dict[str, object],
        resource_table: str = "snapshot",
    ) -> None:
        """Insert a linkage record."""
        lt, _, _ = _table_names(resource_table)
        filtered = {k: v for k, v in payload.items() if k in self._LINKAGE_COLUMNS}
        if not filtered:
            return
        cols = ", ".join(filtered.keys())
        vals = ", ".join(f":{k}" for k in filtered.keys())
        sql = text(f"INSERT INTO {lt} ({cols}) VALUES ({vals})")
        await self.session.execute(sql, filtered)

    async def create_linkage_field(
        self,
        payload: dict[str, object],
        resource_table: str = "snapshot",
    ) -> None:
        """Insert a linkage field record."""
        _, lft, _ = _table_names(resource_table)
        filtered = {k: v for k, v in payload.items() if k in self._LINKAGE_FIELD_COLUMNS}
        if not filtered:
            return
        cols = ", ".join(filtered.keys())
        vals = ", ".join(f":{k}" for k in filtered.keys())
        sql = text(f"INSERT INTO {lft} ({cols}) VALUES ({vals})")
        await self.session.execute(sql, filtered)

    async def update_chart_linkage_active(
        self,
        view_id: int,
        active: bool,
    ) -> None:
        """Update linkage_active on snapshot_core_chart_view.

        Mirrors Java updateLinkageActive which updates snapshot_core_chart_view.
        """
        sql = text("""
            UPDATE snapshot_core_chart_view
            SET linkage_active = :active
            WHERE id = :view_id
        """)
        await self.session.execute(sql, {"active": active, "view_id": view_id})
