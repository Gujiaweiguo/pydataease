"""add log and api_key tables

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f7
Create Date: 2026-05-16 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b2c3d4e5f6a8"
down_revision = "a1b2c3d4e5f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_log_operate",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("uid", sa.BigInteger(), nullable=True),
        sa.Column("oid", sa.BigInteger(), nullable=True),
        sa.Column("op", sa.String(255), nullable=True),
        sa.Column("op_text", sa.String(255), nullable=True),
        sa.Column("op_detail", sa.Text(), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("ip", sa.String(255), nullable=True),
        sa.Column("time", sa.BigInteger(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("msg", sa.Text(), nullable=True),
        sa.Column("resource_id", sa.BigInteger(), nullable=True),
        sa.Column("resource_type", sa.String(255), nullable=True),
        sa.Column("client", sa.String(255), nullable=True),
    )

    op.create_table(
        "xpack_api_key",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("access_key", sa.String(255), nullable=False),
        sa.Column("access_secret", sa.String(255), nullable=False),
        sa.Column("enable", sa.Boolean(), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("creator", sa.BigInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("xpack_api_key")
    op.drop_table("core_log_operate")
