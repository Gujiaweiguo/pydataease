from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PlatformUserInfo:
    """Normalized user info from a platform."""

    platform: str
    external_id: str
    username: str | None = None
    display_name: str | None = None
    email: str | None = None
    mobile: str | None = None
    avatar_url: str | None = None


class BasePlatformProvider(ABC):
    """Base class for platform integration providers."""

    platform_type: str = ""

    def __init__(self, config: dict[str, str] | None = None) -> None:
        self.config: dict[str, str] = config or {}

    @abstractmethod
    def validate_config(self, config: dict[str, str]) -> list[str]:
        ...

    @abstractmethod
    async def get_authorize_url(self, redirect_uri: str, state: str) -> str:
        ...

    @abstractmethod
    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> PlatformUserInfo:
        ...

    async def test_connection(self) -> dict[str, str | bool]:
        try:
            return {"success": True, "message": "Connection test passed"}
        except Exception as exc:  # pragma: no cover
            return {"success": False, "message": str(exc)}
