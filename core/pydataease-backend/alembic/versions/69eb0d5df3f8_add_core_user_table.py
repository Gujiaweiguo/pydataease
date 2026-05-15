"""add core_user table

Revision ID: 69eb0d5df3f8
Revises: 9fabd277b7b0
Create Date: 2026-05-10 00:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "69eb0d5df3f8"
down_revision = "9fabd277b7b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_user",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("account", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("phone_prefix", sa.String(length=255), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("enable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("oid", sa.BigInteger(), nullable=True),
        sa.Column("origin", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("mfa_enable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("language", sa.String(length=255), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_user")),
        sa.UniqueConstraint("account", name=op.f("uq_core_user_account")),
    )
    core_user = sa.table(
        "core_user",
        sa.column("id", sa.BigInteger()),
        sa.column("account", sa.String(length=255)),
        sa.column("name", sa.String(length=255)),
        sa.column("password", sa.String(length=255)),
        sa.column("enable", sa.Boolean()),
        sa.column("oid", sa.BigInteger()),
        sa.column("origin", sa.Integer()),
        sa.column("mfa_enable", sa.Boolean()),
        sa.column("language", sa.String(length=255)),
        sa.column("create_time", sa.BigInteger()),
        sa.column("update_time", sa.BigInteger()),
    )
    op.bulk_insert(
        core_user,
        [
            {
                "id": 1,
                "account": "admin",
                "name": "Administrator",
                "password": "$2b$12$obykRE0U5dPsTV6QXaIvGeO.iFNOHVwIQ1NqxNou5U640WOkbbKdW",
                "enable": True,
                "oid": 1,
                "origin": 0,
                "mfa_enable": False,
                "language": "zh-CN",
                "create_time": 0,
                "update_time": 0,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("core_user")
