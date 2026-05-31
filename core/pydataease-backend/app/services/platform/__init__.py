from __future__ import annotations

from .base import BasePlatformProvider
from .dingtalk_provider import DingTalkPlatformProvider
from .lark_provider import LarkPlatformProvider, LarkSuitePlatformProvider
from .wecom_provider import WeComPlatformProvider

platform_providers: dict[str, type[BasePlatformProvider]] = {
    "wecom": WeComPlatformProvider,
    "dingtalk": DingTalkPlatformProvider,
    "lark": LarkPlatformProvider,
    "larksuite": LarkSuitePlatformProvider,
}


def get_platform_provider(platform: str) -> type[BasePlatformProvider] | None:
    return platform_providers.get(platform)
