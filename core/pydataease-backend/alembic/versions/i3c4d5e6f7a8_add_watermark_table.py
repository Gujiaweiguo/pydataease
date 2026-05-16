"""add visualization_watermark table

Revision ID: i3c4d5e6f7a8
Revises: h2b3c4d5e6f7
Create Date: 2026-05-16 18:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "i3c4d5e6f7a8"
down_revision = "h2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "visualization_watermark",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("version", sa.String(255), nullable=True),
        sa.Column("setting_content", sa.Text(), nullable=True),
        sa.Column("create_by", sa.String(255), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
    )
    # Seed default row matching Java DEFAULT_ID
    op.execute(
        """
        INSERT INTO visualization_watermark (id, version, setting_content, create_by, create_time)
        VALUES ('system_default', NULL, NULL, NULL, NULL)
        ON CONFLICT (id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_table("visualization_watermark")
