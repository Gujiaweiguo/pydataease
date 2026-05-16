"""add geo and sql_log tables

Revision ID: c3d4e5f6a7b9
Revises: b2c3d4e5f6a8
Create Date: 2026-05-16 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c3d4e5f6a7b9"
down_revision = "b2c3d4e5f6a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custom_geo_area",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("create_by", sa.String(255), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_by", sa.String(255), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
    )

    op.create_table(
        "custom_geo_sub_area",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("geo_area_id", sa.String(50), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("geo_json", sa.dialects.postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        "core_dataset_table_sql_log",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("table_id", sa.String(50), nullable=True),
        sa.Column("sql_snapshot", sa.Text(), nullable=True),
        sa.Column("table_name", sa.String(255), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("create_by", sa.String(255), nullable=True),
        sa.Column("status", sa.String(255), nullable=True),
        sa.Column("error_msg", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("core_dataset_table_sql_log")
    op.drop_table("custom_geo_sub_area")
    op.drop_table("custom_geo_area")
