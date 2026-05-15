"""add row permission and whitelist tables

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-05-15 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "b4c5d6e7f8a9"
down_revision = "a3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_row_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("dataset_id", sa.BigInteger(), nullable=False, comment="FK to core_dataset_group.id"),
        sa.Column("target_type", sa.String(length=20), nullable=False, comment="org/role/user/sysvar"),
        sa.Column("target_id", sa.BigInteger(), nullable=False, comment="org_id, role_id, user_id, or 0 for sysvar"),
        sa.Column("filter_sql", sa.Text(), nullable=False, comment="WHERE clause fragment, e.g. region='east'"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_row_permission")),
    )

    op.create_table(
        "core_permission_whitelist",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("dataset_id", sa.BigInteger(), nullable=False, comment="0 means all datasets"),
        sa.Column("scope", sa.String(length=20), nullable=False, comment="row/column/both"),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_permission_whitelist")),
    )

    # Remove server defaults that were only needed for the insert
    op.alter_column("core_row_permission", "enabled", server_default=None)


def downgrade() -> None:
    op.drop_table("core_permission_whitelist")
    op.drop_table("core_row_permission")
