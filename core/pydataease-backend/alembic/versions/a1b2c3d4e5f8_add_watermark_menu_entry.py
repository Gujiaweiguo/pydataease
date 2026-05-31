"""add watermark menu entry

Revision ID: a1b2c3d4e5f8
Revises: 40bf4ea58e3d
Create Date: 2026-05-31 13:35:34.645649

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f8'
down_revision = '40bf4ea58e3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO core_menu (id, pid, type, name, component, menu_sort, icon, path, hidden, in_layout, auth)
        VALUES (1780136996351725193, 15, 1, 'watermark', 'watermark', 7, '', '/watermark', false, true, true)
        ON CONFLICT (id) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM core_menu WHERE id = 1780136996351725193")
