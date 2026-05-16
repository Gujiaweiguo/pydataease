"""add visualization background and subject tables

Revision ID: a1b2c3d4e5f7
Revises: f1a2b3c4d5e6
Create Date: 2026-05-16 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f7"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "visualization_background",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("classification", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("remark", sa.String(255), nullable=True),
        sa.Column("sort", sa.Integer(), nullable=True),
        sa.Column("upload_time", sa.BigInteger(), nullable=True),
        sa.Column("base_url", sa.String(255), nullable=True),
        sa.Column("url", sa.String(255), nullable=True),
    )

    op.create_table(
        "visualization_subject",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("type", sa.String(255), nullable=True),
        sa.Column("details", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("delete_flag", sa.Boolean(), nullable=True),
        sa.Column("cover_url", sa.Text(), nullable=True),
        sa.Column("create_num", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("create_by", sa.String(255), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.Column("update_by", sa.String(255), nullable=True),
        sa.Column("delete_time", sa.BigInteger(), nullable=True),
        sa.Column("delete_by", sa.String(255), nullable=True),
    )

    # Seed background data
    op.execute(
        sa.text(
            "INSERT INTO visualization_background (id, name, classification, content, remark, sort, upload_time, base_url, url) VALUES "
            "('board_1', '边框1', 'default', '', NULL, NULL, NULL, 'img/board', 'board/board_1.svg'), "
            "('board_2', '边框2', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_2.svg'), "
            "('board_3', '边框3', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_3.svg'), "
            "('board_4', '边框4', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_4.svg'), "
            "('board_5', '边框5', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_5.svg'), "
            "('board_6', '边框6', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_6.svg'), "
            "('board_7', '边框7', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_7.svg'), "
            "('board_8', '边框8', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_8.svg'), "
            "('board_9', '边框9', 'default', NULL, NULL, NULL, NULL, 'img/board', 'board/board_9.svg'), "
            "('dark_1', '深色1', 'default', NULL, NULL, NULL, NULL, 'img/dashboard', 'dashboard/dark_1.svg')"
        )
    )


def downgrade() -> None:
    op.drop_table("visualization_subject")
    op.drop_table("visualization_background")
