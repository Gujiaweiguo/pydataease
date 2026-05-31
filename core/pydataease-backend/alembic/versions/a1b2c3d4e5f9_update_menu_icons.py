"""Update icon field for feature-flagged menu entries

Revision ID: a1b2c3d4e5f9
Revises: a1b2c3d4e5f8
Create Date: 2026-05-31
"""
from alembic import op

revision = "a1b2c3d4e5f9"
down_revision = "a1b2c3d4e5f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE core_menu SET icon = 'authentication' WHERE id = 1780136996351725191")
    op.execute("UPDATE core_menu SET icon = 'form' WHERE id = 1780136996351725192")
    op.execute("UPDATE core_menu SET icon = 'watermark' WHERE id = 1780136996351725193")
    op.execute("UPDATE core_menu SET icon = 'variable' WHERE id = 1780196628838721401")


def downgrade() -> None:
    op.execute(
        """
        UPDATE core_menu SET icon = '' WHERE id IN (
            1780136996351725191,
            1780136996351725192,
            1780136996351725193,
            1780196628838721401
        );
        """
    )
