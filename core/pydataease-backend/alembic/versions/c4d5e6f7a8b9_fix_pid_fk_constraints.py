"""fix pid fk constraints

Revision ID: c4d5e6f7a8b9
Revises: b8c9d0e1f2a3
Create Date: 2026-05-12 00:00:00.000000
"""
# pyright: reportUnusedCallResult=false, reportUnknownArgumentType=false

from __future__ import annotations

from alembic import op


revision = "c4d5e6f7a8b9"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("fk_core_datasource_pid_core_datasource", "core_datasource", type_="foreignkey")
    op.create_foreign_key(
        "fk_core_datasource_pid_core_datasource",
        "core_datasource",
        "core_datasource",
        ["pid"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        "INSERT INTO core_datasource (id, name, pid, type, configuration, create_time, update_time, status, task_status) "
        "VALUES (0, 'root', NULL, 'folder', '{}', 0, 0, 'Success', 'WaitingForExecution') "
        "ON CONFLICT (id) DO NOTHING"
    )

    op.drop_constraint("fk_core_dataset_group_pid_core_dataset_group", "core_dataset_group", type_="foreignkey")
    op.create_foreign_key(
        "fk_core_dataset_group_pid_core_dataset_group",
        "core_dataset_group",
        "core_dataset_group",
        ["pid"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        "INSERT INTO core_dataset_group (id, name, pid, node_type, type, mode, create_time, last_update_time) "
        "VALUES (0, 'root', NULL, 'folder', 'db', 0, 0, 0) "
        "ON CONFLICT (id) DO NOTHING"
    )


def downgrade() -> None:
    op.execute("DELETE FROM core_dataset_group WHERE id = 0")
    op.execute("DELETE FROM core_datasource WHERE id = 0")

    op.drop_constraint("fk_core_dataset_group_pid_core_dataset_group", "core_dataset_group", type_="foreignkey")
    op.create_foreign_key(
        "fk_core_dataset_group_pid_core_dataset_group",
        "core_dataset_group",
        "core_dataset_group",
        ["pid"],
        ["id"],
    )

    op.drop_constraint("fk_core_datasource_pid_core_datasource", "core_datasource", type_="foreignkey")
    op.create_foreign_key(
        "fk_core_datasource_pid_core_datasource",
        "core_datasource",
        "core_datasource",
        ["pid"],
        ["id"],
    )
