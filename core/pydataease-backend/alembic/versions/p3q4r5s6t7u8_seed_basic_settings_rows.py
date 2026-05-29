"""seed basic.* settings rows

Revision ID: p3q4r5s6t7u8
Revises: o2p3q4r5s6t7
Create Date: 2026-05-29

These rows are required by the frontend BasicInfo.vue page.
All keys are prefixed with 'basic.' so the backend query_basic_settings()
can filter them with WHERE setting_key LIKE 'basic.%'.
"""

from alembic import op

revision = "p3q4r5s6t7u8"
down_revision = "o2p3q4r5s6t7"
branch_labels = None
depends_on = None

# Default values for the 22 basic settings expected by the frontend.
# See: BasicInfo.vue, BasicEdit.vue, zh-CN.ts (setting_basic.* i18n keys)
_BASIC_SETTINGS = [
    ("basic.dsIntervalTime", "30"),
    ("basic.dsExecuteTime", "minute"),
    ("basic.frontTimeOut", "30"),
    ("basic.logLiveTime", "180"),
    ("basic.thresholdLogLiveTime", "180"),
    ("basic.dataFillingLogLiveTime", "180"),
    ("basic.exportFileLiveTime", "180"),
    ("basic.thresholdLimit", "30"),
    ("basic.platformOid", ""),
    ("basic.platformRid", ""),
    ("basic.pwdStrategy", "false"),
    ("basic.dip", "false"),
    ("basic.pvp", "0"),
    ("basic.defaultLogin", "0"),
    ("basic.autoCreateUser", "false"),
    ("basic.shareDisable", "false"),
    ("basic.sharePeRequire", "false"),
    ("basic.defaultSort", "1"),
    ("basic.defaultOpen", "0"),
    ("basic.loginLimit", "false"),
    ("basic.loginLimitRate", "5"),
    ("basic.loginLimitTime", "30"),
]


def upgrade() -> None:
    for key, value in _BASIC_SETTINGS:
        op.execute(
            f"""
            INSERT INTO core_sys_setting (setting_key, setting_value, type)
            VALUES ('{key}', '{value}', 'basic')
            ON CONFLICT (setting_key) DO NOTHING
            """
        )


def downgrade() -> None:
    op.execute(
        "DELETE FROM core_sys_setting WHERE setting_key LIKE 'basic.%'"
    )
