"""add column permission table

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-05-15 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "c5d6e7f8a9b0"
down_revision = "b4c5d6e7f8a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_column_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("dataset_id", sa.BigInteger(), nullable=False, comment="FK to core_dataset_group.id"),
        sa.Column("field_id", sa.BigInteger(), nullable=False, comment="FK to core_dataset_table_field.id"),
        sa.Column("target_type", sa.String(length=20), nullable=False, comment="org/role/user"),
        sa.Column("target_id", sa.BigInteger(), nullable=False, comment="org_id, role_id, or user_id"),
        sa.Column("action", sa.String(length=20), nullable=False, comment="disable/desensitize/mask"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_column_permission")),
    )

    # Remove server default that was only needed for the insert
    op.alter_column("core_column_permission", "enabled", server_default=None)


def downgrade() -> None:
    op.drop_table("core_column_permission")
