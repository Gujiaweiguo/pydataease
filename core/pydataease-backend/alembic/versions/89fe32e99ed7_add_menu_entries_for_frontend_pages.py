"""add_menu_entries_for_frontend_pages

Revision ID: 89fe32e99ed7
Revises: 7aafbb0a9ea0
Create Date: 2026-05-30 18:30:19.622002

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '89fe32e99ed7'
down_revision = '7aafbb0a9ea0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO core_menu (id, pid, type, name, component, menu_sort, icon, path, hidden, in_layout, auth)
        VALUES
          (1780136996351725191, 15, 1, 'auth-provider', 'system/auth-provider', 5, '', '/auth-provider', false, true, true),
          (1780136996351725192, 15, 1, 'data-filing', 'data-filing', 6, '', '/data-filing', false, true, true)
        ON CONFLICT (id) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM core_menu WHERE id IN (1780136996351725191, 1780136996351725192)
    """)
