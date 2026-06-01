"""add user_id to sys variable value

Revision ID: f1a2b3c4d5e7
Revises: e7f8a9b0c1d2
Create Date: 2026-06-01 12:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "f1a2b3c4d5e7"
down_revision = "e7f8a9b0c1d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("core_sys_variable_value", sa.Column("user_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("core_sys_variable_value", "user_id")
