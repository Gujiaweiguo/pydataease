"""add mask range to column permission

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-05-31 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "d6e7f8a9b0c1"
down_revision = "c5d6e7f8a9b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "core_column_permission",
        sa.Column(
            "mask_start",
            sa.Integer(),
            nullable=True,
            comment="Start position for mask action (0-indexed)",
        ),
    )
    op.add_column(
        "core_column_permission",
        sa.Column(
            "mask_end",
            sa.Integer(),
            nullable=True,
            comment="End position for mask action (exclusive)",
        ),
    )


def downgrade() -> None:
    op.drop_column("core_column_permission", "mask_end")
    op.drop_column("core_column_permission", "mask_start")
