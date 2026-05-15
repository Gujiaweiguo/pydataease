"""create core_sys_setting table

Revision ID: b8c9d0e1f2a3
Revises: a1b2c3d4e5f6
Create Date: 2026-05-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "b8c9d0e1f2a3"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_sys_setting",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("setting_key", sa.String(255), nullable=False, unique=True),
        sa.Column("setting_value", sa.Text(), nullable=True),
        sa.Column("type", sa.String(50), nullable=True),
    )
    op.execute(
        """
        INSERT INTO core_sys_setting (setting_key, setting_value, type) VALUES
        ('ui.themeColor', '#1B5EBF', 'ui'),
        ('ui.customColor', '', 'ui'),
        ('ui.navigateBg', '#FFFFFF', 'ui'),
        ('ui.navigate', 'left', 'ui'),
        ('ui.mobileLogin', '0', 'ui'),
        ('ui.mobileLoginBg', '', 'ui'),
        ('ui.bg', '', 'ui'),
        ('ui.login', '0', 'ui'),
        ('ui.showSlogan', '1', 'ui'),
        ('ui.slogan', '', 'ui'),
        ('ui.web', '', 'ui'),
        ('ui.name', '', 'ui'),
        ('ui.foot', '0', 'ui'),
        ('ui.footContent', '', 'ui'),
        ('defaultSettings.sort', 'asc', 'setting'),
        ('shareBase.disable', 'true', 'setting'),
        ('shareBase.peRequire', 'false', 'setting'),
        ('i18nOptions', '{}', 'setting'),
        ('requestTimeOut', '120', 'setting'),
        ('defaultLogin', '0', 'setting')
        """
    )


def downgrade() -> None:
    op.drop_table("core_sys_setting")
