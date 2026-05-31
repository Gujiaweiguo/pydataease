"""add my filing menu entry

Revision ID: b1c2d3e4f5a0
Revises: a1b2c3d4e5f9
Create Date: 2026-05-31
"""
from __future__ import annotations

from alembic import op

revision = 'b1c2d3e4f5a0'
down_revision = 'a1b2c3d4e5f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET session_replication_role = 'replica';")
    op.execute(
        """
        INSERT INTO core_menu (id, pid, type, name, component, menu_sort, icon, path, hidden, in_layout, auth)
        VALUES (1780214879339311535, 0, 1, 'my-filing', 'data-filing/MyFiling', 6, 'form', '/my-filing', false, true, false)
        ON CONFLICT (id) DO NOTHING
        """
    )
    op.execute("SET session_replication_role = 'origin';")


def downgrade() -> None:
    op.execute("DELETE FROM core_menu WHERE id = 1780214879339311535")
