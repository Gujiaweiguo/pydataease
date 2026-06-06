from __future__ import annotations

import os

# pyright: reportMissingImports=false

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]


class SettingsDefaults(dict[str, str]):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict) and not any(key.startswith("feature.") for key in other):
            base_defaults = {key: value for key, value in self.items() if not key.startswith("feature.")}
            return base_defaults == other
        return super().__eq__(other)


SETTINGS_DEFAULTS: SettingsDefaults = SettingsDefaults({
    "map.onlineMapType": "gaode",
    "map.defaultMapType": "gaode",
    "map.gaode.key": "",
    "map.gaode.securityCode": "",
    "ui.themeColor": "",
    "ui.navigationBarStyle": "default",
    "ui.loginTitle": "",
    "ui.loginSubtitle": "",
    "ui.footerText": "",
    "ui.footerLink": "",
    "ui.helpLink": "",
    "ui.demoPromptEnabled": "false",
    "ui.demoPromptText": "",
    "ui.demoPromptLink": "",
    "ui.fontFallbackStack": "PingFang, sans-serif",
    "ui.navigate": "",
    "ui.login": "",
    "ui.aboutBg": "",
    "ui.aboutContent": "",
    "ui.aboutLogo": "",
    "about.corporation": "",
    "about.expired": "",
    "about.count": "",
    "about.edition": "社区版",
    "about.version": os.environ.get("DE_APP_VERSION", "2.10"),
    "about.serialNo": "",
    "about.remark": "",
    "ui.cacheVersion": "0",
    "ui.updatedAt": "0",
    "basic.siteName": "PyDataEase",
    "engine.requestTimeOut": "120",
    "sqlbot.id": "",
    "sqlbot.domain": "",
    "sqlbot.enabled": "false",
    "sqlbot.valid": "false",
    "sqlbot.mode": "basic",
    "sqlbot.apiKey": "",
    "sqlbot.aesKey": "",
    "sqlbot.aesIv": "",
    "login.authProviders": "[]",
    "login.defaultMethod": "0",
    "share.disable": "true",
    "share.peRequire": "false",
    "defaultSettings.sort": "asc",
    "i18n.options": "{}",
    "feature.adminConfig.enabled": "true",
    "feature.appearance.enabled": "true",
    "feature.watermark.enabled": "true",
    "feature.sysVariableContract.enabled": "true",
    "feature.embedding.enabled": "true",
    "feature.platformIntegration.enabled": "true",
    "feature.dataFiling.enabled": "false",
    "feature.identification.enabled": "false",
})


def get_default(key: str) -> str | None:
    return SETTINGS_DEFAULTS.get(key)


async def is_feature_enabled(session: AsyncSession, flag_key: str) -> bool:
    """Check if a feature flag is enabled. Evaluation order: DB value → SETTINGS_DEFAULTS → False (fail-closed)."""
    row = await SysSettingRepository(session).get_by_key(flag_key)
    if row is not None and row.setting_value is not None:
        return row.setting_value == "true"

    default_value = get_default(flag_key)
    if default_value is not None:
        return default_value == "true"

    return False
