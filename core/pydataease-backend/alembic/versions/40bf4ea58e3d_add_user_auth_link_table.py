"""add_user_auth_link_table

Revision ID: 40bf4ea58e3d
Revises: 89fe32e99ed7
Create Date: 2026-05-30 23:31:39.896613

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '40bf4ea58e3d'
down_revision = '89fe32e99ed7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_user_auth_link",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("provider_id", sa.BigInteger(), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("external_username", sa.String(255), nullable=True),
        sa.Column("external_email", sa.String(255), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("provider_id", "external_id", name="uq_provider_external"),
    )


def downgrade() -> None:
    op.drop_table("core_user_auth_link")
