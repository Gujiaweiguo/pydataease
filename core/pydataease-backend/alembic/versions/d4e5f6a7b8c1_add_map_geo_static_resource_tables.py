"""add map_geo and static_resource tables

Revision ID: d4e5f6a7b8c1
Revises: c3d4e5f6a7b9
Create Date: 2026-05-16 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "d4e5f6a7b8c1"
down_revision = "c3d4e5f6a7b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "map_geo",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("geo_json", sa.dialects.postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        "static_resource",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("static_resource")
    op.drop_table("map_geo")
