"""add visualization template tables

Revision ID: f1a2b3c4d5e6
Revises: e6f7a8b9c0d1
Create Date: 2026-05-16 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f1a2b3c4d5e6"
down_revision = "e6f7a8b9c0d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "visualization_template",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("pid", sa.String(255), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("dv_type", sa.String(255), nullable=True),
        sa.Column("node_type", sa.String(255), nullable=True),
        sa.Column("create_by", sa.String(255), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("snapshot", sa.Text(), nullable=True),
        sa.Column("template_type", sa.String(255), nullable=True),
        sa.Column("template_style", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("template_data", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("dynamic_data", sa.dialects.postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        "visualization_template_category",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("pid", sa.String(255), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("dv_type", sa.String(255), nullable=True),
        sa.Column("node_type", sa.String(255), nullable=True),
        sa.Column("create_by", sa.String(255), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("snapshot", sa.Text(), nullable=True),
        sa.Column("template_type", sa.String(255), nullable=True),
    )

    op.create_table(
        "visualization_template_category_map",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("category_id", sa.String(255), nullable=True),
        sa.Column("template_id", sa.String(255), nullable=True),
    )

    # Seed default category
    op.execute(
        sa.text(
            "INSERT INTO visualization_template_category "
            "(id, name, pid, level, dv_type, node_type, create_by, create_time, snapshot, template_type) "
            "VALUES ('default', '默认分类', '0', 0, 'dashboard', 'folder', NULL, NULL, NULL, 'system')"
        )
    )


def downgrade() -> None:
    op.drop_table("visualization_template_category_map")
    op.drop_table("visualization_template_category")
    op.drop_table("visualization_template")
