"""Clean up test data, keeping only official demo datasource, dataset, and dashboard.

Demo data to keep:
  - Datasource: Demo PG (id=1778561566975586637) + root folder (id=0)
  - Dataset: Demo Dataset (id=1778561592457469007) + root folder (id=0)
  - Dataset Table: core_menu (id=1778561592490907630)
  - Dashboard: Demo Dashboard (id=1778561641707434266)
  - xpack_share for Demo Dashboard (resource_id=1778561641707434266)

Usage:
    DE_ENV=dev uv run python scripts/cleanup_test_data.py
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text

from app.dependencies.database import async_session

logger = logging.getLogger(__name__)

# ---- Demo IDs to KEEP ----
KEEP_DATASOURCE_IDS = {0, 1778561566975586637}
KEEP_DATASET_GROUP_IDS = {0, 1778561592457469007}
KEEP_DATASET_TABLE_IDS = {1778561592490907630}
KEEP_VISUALIZATION_IDS = {1778561641707434266}
KEEP_XPACK_SHARE_IDS = {
    # resource_id mapping to find which to keep — we keep the demo dashboard share
}
# xpack_share rows to keep (by resource_id)
KEEP_XPACK_SHARE_RESOURCE_IDS = {1778561641707434266}

# ---- Tables that may reference the above ----
# We do NOT delete system-level tables: core_user, core_org, core_role, etc.


async def count_table(session, table: str) -> int:
    result = await session.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
    return result.scalar()


async def get_all_ids(session, table: str, id_col: str = "id") -> set[int]:
    result = await session.execute(text(f'SELECT "{id_col}" FROM "{table}"'))
    return {row[0] for row in result}


async def delete_by_ids(session, table: str, ids: set[int], id_col: str = "id") -> int:
    if not ids:
        return 0
    ids_list = sorted(ids)
    # Delete in batches to avoid huge SQL
    total = 0
    for i in range(0, len(ids_list), 100):
        batch = ids_list[i : i + 100]
        placeholders = ",".join(str(x) for x in batch)
        result = await session.execute(
            text(f'DELETE FROM "{table}" WHERE "{id_col}" IN ({placeholders})')
        )
        total += result.rowcount
    return total


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("Starting test data cleanup...\n")

    async with async_session() as session:
        async with session.begin():
            # ── Step 1: core_chart_view ──
            before = await count_table(session, "core_chart_view")
            logger.info("core_chart_view before: %d", before)
            all_chart_ids = await get_all_ids(session, "core_chart_view")
            if all_chart_ids:
                deleted = await delete_by_ids(session, "core_chart_view", all_chart_ids)
                logger.info("  Deleted %d chart views (all are test data)", deleted)

            # ── Step 2: core_dataset_table_field ──
            before = await count_table(session, "core_dataset_table_field")
            logger.info("core_dataset_table_field before: %d", before)
            result = await session.execute(
                text(
                    'SELECT id FROM core_dataset_table_field '
                    f'WHERE dataset_group_id NOT IN ({",".join(str(x) for x in KEEP_DATASET_GROUP_IDS)})'
                )
            )
            field_ids_to_delete = {row[0] for row in result}
            if field_ids_to_delete:
                deleted = await delete_by_ids(session, "core_dataset_table_field", field_ids_to_delete)
                logger.info("  Deleted %d test dataset table fields", deleted)

            # ── Step 3: core_dataset_table_sql_log ──
            before = await count_table(session, "core_dataset_table_sql_log")
            if before > 0:
                result = await session.execute(
                    text(
                        'SELECT id FROM core_dataset_table_sql_log '
                        f'WHERE dataset_group_id NOT IN ({",".join(str(x) for x in KEEP_DATASET_GROUP_IDS)})'
                    )
                )
                log_ids = {row[0] for row in result}
                if log_ids:
                    await delete_by_ids(session, "core_dataset_table_sql_log", log_ids)
            logger.info("core_dataset_table_sql_log: cleaned")

            # ── Step 4: core_dataset_table ──
            before = await count_table(session, "core_dataset_table")
            logger.info("core_dataset_table before: %d", before)
            result = await session.execute(
                text(
                    'SELECT id FROM core_dataset_table '
                    f'WHERE id NOT IN ({",".join(str(x) for x in KEEP_DATASET_TABLE_IDS)})'
                )
            )
            table_ids_to_delete = {row[0] for row in result}
            if table_ids_to_delete:
                deleted = await delete_by_ids(session, "core_dataset_table", table_ids_to_delete)
                logger.info("  Deleted %d test dataset tables", deleted)

            # ── Step 5: core_datasource_task_log & core_datasource_task ──
            for tbl in ("core_datasource_task_log", "core_datasource_task"):
                cnt = await count_table(session, tbl)
                if cnt > 0:
                    result = await session.execute(
                        text(
                            f'SELECT id FROM "{tbl}" '
                            f'WHERE ds_id NOT IN ({",".join(str(x) for x in KEEP_DATASOURCE_IDS)})'
                        )
                    )
                    ids = {row[0] for row in result}
                    if ids:
                        await delete_by_ids(session, tbl, ids)
                logger.info("%s: cleaned", tbl)

            # ── Step 6: xpack_share — delete shares for test resources ──
            before = await count_table(session, "xpack_share")
            logger.info("xpack_share before: %d", before)
            result = await session.execute(
                text(
                    'SELECT id FROM xpack_share '
                    f'WHERE resource_id NOT IN ({",".join(str(x) for x in KEEP_XPACK_SHARE_RESOURCE_IDS)})'
                )
            )
            share_ids_to_delete = {row[0] for row in result}
            if share_ids_to_delete:
                deleted = await delete_by_ids(session, "xpack_share", share_ids_to_delete)
                logger.info("  Deleted %d test shares", deleted)

            # ── Step 7: data_visualization_info (dashboards, panels) ──
            before = await count_table(session, "data_visualization_info")
            logger.info("data_visualization_info before: %d", before)
            result = await session.execute(
                text(
                    'SELECT id FROM data_visualization_info '
                    f'WHERE id NOT IN ({",".join(str(x) for x in KEEP_VISUALIZATION_IDS)})'
                )
            )
            vis_ids_to_delete = {row[0] for row in result}
            if vis_ids_to_delete:
                deleted = await delete_by_ids(session, "data_visualization_info", vis_ids_to_delete)
                logger.info("  Deleted %d test dashboards/panels", deleted)

            # ── Step 8: core_dataset_group (folders + datasets) ──
            count_ds_before = await count_table(session, "core_dataset_group")
            logger.info("core_dataset_group before: %d", count_ds_before)
            result = await session.execute(
                text(
                    'SELECT id FROM core_dataset_group '
                    f'WHERE id NOT IN ({",".join(str(x) for x in KEEP_DATASET_GROUP_IDS)})'
                )
            )
            ds_group_ids = {row[0] for row in result}
            if ds_group_ids:
                deleted = await delete_by_ids(session, "core_dataset_group", ds_group_ids)
                logger.info("  Deleted %d test dataset groups", deleted)

            # ── Step 9: core_datasource ──
            count_ds_before = await count_table(session, "core_datasource")
            logger.info("core_datasource before: %d", count_ds_before)
            result = await session.execute(
                text(
                    'SELECT id FROM core_datasource '
                    f'WHERE id NOT IN ({",".join(str(x) for x in KEEP_DATASOURCE_IDS)})'
                )
            )
            ds_ids_to_delete = {row[0] for row in result}
            if ds_ids_to_delete:
                deleted = await delete_by_ids(session, "core_datasource", ds_ids_to_delete)
                logger.info("  Deleted %d test datasources", deleted)

        # ── After commit, verify ──
        logger.info("\n=== Cleanup complete. Verifying... ===\n")

        tables_to_verify = [
            "core_chart_view",
            "core_dataset_table_field",
            "core_dataset_table",
            "core_dataset_group",
            "core_datasource",
            "data_visualization_info",
            "xpack_share",
        ]
        for tbl in tables_to_verify:
            after = await count_table(session, tbl)
            logger.info("  %s: %d rows remaining", tbl, after)

        # Show what's left
        logger.info("\n=== Remaining datasources ===")
        result = await session.execute(text("SELECT id, name, type FROM core_datasource"))
        for row in result:
            logger.info("  id=%s name=%s type=%s", row.id, row.name, row.type)

        logger.info("\n=== Remaining dataset groups ===")
        result = await session.execute(text("SELECT id, name, node_type FROM core_dataset_group"))
        for row in result:
            logger.info("  id=%s name=%s node_type=%s", row.id, row.name, row.node_type)

        logger.info("\n=== Remaining data_visualization_info ===")
        result = await session.execute(text("SELECT id, name, type FROM data_visualization_info"))
        for row in result:
            logger.info("  id=%s name=%s type=%s", row.id, row.name, row.type)


if __name__ == "__main__":
    asyncio.run(main())
