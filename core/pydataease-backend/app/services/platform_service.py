from __future__ import annotations

from typing import Any, cast

from fastapi import Depends  # pyright: ignore[reportMissingImports]
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.models.auth_provider import AuthProvider  # pyright: ignore[reportImplicitRelativeImport]
from app.models.user_auth_link import UserAuthLink  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.user_auth_link_repo import UserAuthLinkRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.services.auth_provider.base import ProviderClaim  # pyright: ignore[reportImplicitRelativeImport]
from app.services.auth_service import AuthService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform import get_platform_provider  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform.base import PlatformUserInfo  # pyright: ignore[reportImplicitRelativeImport]
from app.services.user_provisioning_service import UserProvisioningService  # pyright: ignore[reportImplicitRelativeImport]

PLATFORM_ORIGIN_MAP: dict[str, int] = {"wecom": 4, "dingtalk": 5, "lark": 6, "larksuite": 7}
SECRET_KEYS = {"secret", "appSecret"}


class PlatformService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.setting_repo = SysSettingRepository(session)
        self.auth_link_repo = UserAuthLinkRepository(session)

    async def get_platform_config(self, platform: str) -> dict[str, str]:
        prefix = f"platform.{platform}."
        rows = await self.setting_repo.list_by_prefix(prefix)
        result: dict[str, str] = {}
        for row in rows:
            key = row.setting_key[len(prefix) :]
            value = row.setting_value or ""
            result[key] = self._mask(value) if key in SECRET_KEYS else value
        return result

    async def save_platform_config(self, platform: str, config: dict[str, str]) -> None:
        for key, value in config.items():
            await self.setting_repo.upsert(f"platform.{platform}.{key}", value, "platform")

    async def validate_platform(self, platform: str) -> dict[str, object]:
        config = await self.get_platform_config_raw(platform)
        provider = self._build_provider(platform, config)
        errors = provider.validate_config(config)
        if errors:
            return {"success": False, "message": "; ".join(errors)}
        return cast(dict[str, object], await provider.test_connection())

    async def get_qr_url(self, platform: str, redirect_uri: str, state: str) -> str:
        provider = self._build_provider(platform, await self.get_platform_config_raw(platform))
        return await provider.get_authorize_url(redirect_uri, state)

    async def handle_platform_login(self, platform: str, code: str, state: str, redirect_uri: str) -> dict[str, object]:
        provider = self._build_provider(platform, await self.get_platform_config_raw(platform))
        user_info = await provider.handle_callback(code, state, redirect_uri)
        origin = PLATFORM_ORIGIN_MAP.get(platform, 9)

        provisioning = UserProvisioningService(self.session)
        user = await self._find_or_create_user(provisioning, platform, origin, user_info)
        if user is None:
            raise ValueError(f"Failed to provision user from {platform}")
        if not user.enable:
            raise ValueError("User account is disabled")

        await self._create_or_update_link(provisioning, user.id, origin, user_info)

        auth_service = AuthService(self.session)
        oid = await auth_service._resolve_current_org_id(user.id, user.oid or 0)
        token = auth_service._issue_token(user.id, oid, user.password)
        await self.session.commit()
        return {"token": token.token, "exp": token.exp}

    async def bind_platform(self, user_id: int, platform: str, code: str, state: str, redirect_uri: str) -> None:
        provider = self._build_provider(platform, await self.get_platform_config_raw(platform))
        user_info = await provider.handle_callback(code, state, redirect_uri)
        await self._upsert_binding(user_id, PLATFORM_ORIGIN_MAP.get(platform, 9), user_info)
        await self.session.commit()

    async def unbind_platform(self, user_id: int, platform: str) -> None:
        origin = PLATFORM_ORIGIN_MAP.get(platform, 9)
        await self.session.execute(delete(UserAuthLink).where(UserAuthLink.user_id == user_id, UserAuthLink.provider_id == origin))
        await self.session.commit()

    async def get_platform_bindings(self, user_id: int) -> list[dict[str, object]]:
        links = await self.auth_link_repo.list_by_user(user_id)
        origin_map = {value: key for key, value in PLATFORM_ORIGIN_MAP.items()}
        result: list[dict[str, object]] = []
        for link in links:
            platform = origin_map.get(link.provider_id)
            if platform is not None:
                result.append({"platform": platform, "externalId": link.external_id, "origin": link.provider_id})
        return result

    async def get_platform_config_raw(self, platform: str) -> dict[str, str]:
        prefix = f"platform.{platform}."
        rows = await self.setting_repo.list_by_prefix(prefix)
        return {row.setting_key[len(prefix) :]: row.setting_value or "" for row in rows}

    async def _find_or_create_user(
        self,
        provisioning: UserProvisioningService,
        platform: str,
        origin: int,
        user_info: PlatformUserInfo,
    ) -> Any:
        link = await provisioning.link_repo.get_by_provider_and_external_id(origin, user_info.external_id)
        if link is not None:
            return await provisioning.user_repo.get_by_id(link.user_id)

        user = await provisioning.user_repo.get_by_email(user_info.email) if user_info.email else None
        if user is not None:
            return user

        created = await provisioning._create_user(
            ProviderClaim(
                external_id=user_info.external_id,
                username=user_info.username,
                email=user_info.email,
                display_name=user_info.display_name,
            ),
            origin,
            AuthProvider(
                id=origin,
                name=platform,
                type=platform,
                config={},
                claim_mapping={},
                enabled=True,
                is_default=False,
                oid=0,
            ),
        )
        if isinstance(created, str):
            raise ValueError(created)
        return created

    async def _create_or_update_link(
        self,
        provisioning: UserProvisioningService,
        user_id: int,
        origin: int,
        user_info: PlatformUserInfo,
    ) -> None:
        existing = await provisioning.link_repo.get_by_provider_and_external_id(origin, user_info.external_id)
        payload = {
            "user_id": user_id,
            "provider_id": origin,
            "external_id": user_info.external_id,
            "external_username": user_info.username,
            "external_email": user_info.email,
        }
        if existing is not None:
            await provisioning.link_repo.update(existing, payload)
        else:
            await provisioning.link_repo.create(payload)

    async def _upsert_binding(self, user_id: int, origin: int, user_info: PlatformUserInfo) -> None:
        existing = await self.auth_link_repo.get_by_user_and_provider(user_id, origin)
        payload = {
            "user_id": user_id,
            "provider_id": origin,
            "external_id": user_info.external_id,
            "external_username": user_info.username,
            "external_email": user_info.email,
        }
        if existing is not None:
            await self.auth_link_repo.update(existing, payload)
        else:
            await self.auth_link_repo.create(payload)

    def _build_provider(self, platform: str, config: dict[str, str]):
        provider_cls = get_platform_provider(platform)
        if provider_cls is None:
            raise ValueError(f"Unknown platform: {platform}")
        return provider_cls(config)

    @staticmethod
    def _mask(value: str) -> str:
        if not value or len(value) < 8:
            return "****"
        return value[:4] + "****" + value[-4:]


def get_platform_service(session: AsyncSession = Depends(get_db)) -> PlatformService:
    return PlatformService(session)
