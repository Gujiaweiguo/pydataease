from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.models.auth_provider import AuthProvider
from app.repositories.auth_provider_repo import AuthProviderRepository
from app.services.auth_provider import get_provider_class
from app.services.auth_provider.base import AuthResult
from app.settings.defaults import is_feature_enabled

logger = logging.getLogger(__name__)


class AuthProviderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AuthProviderRepository(session)

    # --- List / Query ---

    async def list_providers(self, enabled_only: bool = False) -> list[dict[str, Any]]:
        """List providers as status dicts."""
        providers = await self.repo.get_all(enabled_only=enabled_only)
        result = []
        for p in providers:
            result.append({
                "id": p.id,
                "name": p.name,
                "type": p.type,
                "enabled": p.enabled,
                "isDefault": p.is_default,
                "oid": p.oid,
            })
        return result

    async def get_provider(self, provider_id: int) -> dict[str, Any] | None:
        provider = await self.repo.get_by_id(provider_id)
        if provider is None:
            return None
        return {
            "id": provider.id,
            "name": provider.name,
            "type": provider.type,
            "config": provider.config or {},
            "claimMapping": provider.claim_mapping or {},
            "enabled": provider.enabled,
            "isDefault": provider.is_default,
            "oid": provider.oid,
            "createTime": str(provider.create_time) if provider.create_time else None,
            "updateTime": str(provider.update_time) if provider.update_time else None,
        }

    async def get_auth_status(self) -> list[dict[str, Any]]:
        """Build the authentication status for bootstrap endpoint.

        Always includes 'local' as a synthetic provider.
        Only includes external providers when feature.identification.enabled is True.
        """
        # Always include local login
        status: list[dict[str, Any]] = [
            {"type": "local", "name": "本地登录", "enabled": True, "isDefault": False}
        ]

        # Check feature flag
        feature_on = await is_feature_enabled(self.session, "feature.identification.enabled")
        if not feature_on:
            # Feature disabled: local is default, no external providers shown
            status[0]["isDefault"] = True
            return status

        # Get enabled providers
        providers = await self.repo.get_all(enabled_only=True)
        has_external_default = False
        for p in providers:
            status.append({
                "id": p.id,
                "type": p.type,
                "name": p.name,
                "enabled": p.enabled,
                "isDefault": p.is_default,
            })
            if p.is_default:
                has_external_default = True

        # If no external provider is default, local is default
        if not has_external_default:
            status[0]["isDefault"] = True

        return status

    # --- CRUD ---

    async def create_provider(self, payload: dict[str, Any]) -> dict[str, Any] | str:
        """Create a new auth provider. Returns provider dict or error string."""
        provider_type = payload.get("type", "")
        name = payload.get("name", "")

        # Validate type
        provider_cls = get_provider_class(provider_type)
        if provider_cls is None:
            return f"Unknown provider type: {provider_type}"

        if not name:
            return "Provider name is required"

        # Validate config
        config = payload.get("config", {})
        provider_instance = provider_cls(config)
        errors = provider_instance.validate_config(config)
        if errors:
            return f"Config validation failed: {'; '.join(errors)}"

        # Create model
        is_default = payload.get("isDefault", False)
        provider = AuthProvider(
            id=time.time_ns(),
            name=name,
            type=provider_type,
            config=config,
            claim_mapping=payload.get("claimMapping", {}),
            enabled=payload.get("enabled", False),
            is_default=is_default,
            oid=payload.get("oid"),
        )

        # If setting as default, clear others first
        if is_default:
            await self.repo.clear_all_defaults()
            await self.session.commit()

        created = await self.repo.create(provider)
        return await self.get_provider(created.id)  # type: ignore[arg-type]

    async def update_provider(self, provider_id: int, payload: dict[str, Any]) -> dict[str, Any] | str:
        """Update an auth provider. Returns provider dict or error string."""
        provider = await self.repo.get_by_id(provider_id)
        if provider is None:
            return f"Provider not found: {provider_id}"

        updates: dict[str, Any] = {}

        if "name" in payload:
            updates["name"] = payload["name"]

        if "type" in payload:
            provider_cls = get_provider_class(payload["type"])
            if provider_cls is None:
                return f"Unknown provider type: {payload['type']}"
            updates["type"] = payload["type"]

        if "config" in payload:
            config = payload["config"]
            ptype = updates.get("type", provider.type)
            provider_cls = get_provider_class(ptype)
            if provider_cls:
                errors = provider_cls(config).validate_config(config)
                if errors:
                    return f"Config validation failed: {'; '.join(errors)}"
            updates["config"] = config

        if "claimMapping" in payload:
            updates["claim_mapping"] = payload["claimMapping"]

        if "enabled" in payload:
            updates["enabled"] = payload["enabled"]

        if "isDefault" in payload:
            if payload["isDefault"]:
                await self.repo.clear_all_defaults()
                await self.session.commit()
            updates["is_default"] = payload["isDefault"]

        if "oid" in payload:
            updates["oid"] = payload["oid"]

        result = await self.repo.update(provider_id, **updates)
        if result is None:
            return f"Provider not found: {provider_id}"
        return await self.get_provider(result.id)

    async def delete_provider(self, provider_id: int) -> bool | str:
        """Delete a provider. Returns True on success or error string."""
        provider = await self.repo.get_by_id(provider_id)
        if provider is None:
            return f"Provider not found: {provider_id}"

        if provider.is_default:
            return "Cannot delete the default provider. Set another provider as default first."

        return await self.repo.delete(provider_id)

    async def toggle_provider(self, provider_id: int, enabled: bool) -> dict[str, Any] | str:
        """Enable or disable a provider."""
        result = await self.repo.update(provider_id, enabled=enabled)
        if result is None:
            return f"Provider not found: {provider_id}"
        return await self.get_provider(result.id)

    async def set_default_provider(self, provider_id: int) -> dict[str, Any] | str:
        """Atomically set a provider as default (clearing previous default)."""
        provider = await self.repo.get_by_id(provider_id)
        if provider is None:
            return f"Provider not found: {provider_id}"

        if not provider.enabled:
            return "Cannot set a disabled provider as default"

        await self.repo.clear_all_defaults()
        await self.session.commit()

        result = await self.repo.update(provider_id, is_default=True)
        if result is None:
            return f"Provider not found: {provider_id}"
        return await self.get_provider(result.id)

    # --- Authentication ---

    async def authenticate_with_provider(self, provider_id: int, credentials: dict) -> AuthResult | str:
        """Authenticate using a specific provider."""
        provider = await self.repo.get_by_id(provider_id)
        if provider is None:
            return f"Provider not found: {provider_id}"

        if not provider.enabled:
            return AuthResult(success=False, error="Provider is disabled")

        provider_cls = get_provider_class(provider.type)
        if provider_cls is None:
            return AuthResult(success=False, error=f"Unknown provider type: {provider.type}")

        instance = provider_cls(provider.config or {})
        result = await instance.authenticate(credentials)

        if result.success and result.claims:
            # Apply claim mapping if configured
            result.claims = self._apply_claim_mapping(result.claims, provider.claim_mapping or {})

        return result

    async def handle_provider_callback(self, provider_id: int, code: str, state: str, redirect_uri: str) -> AuthResult | str:
        """Handle OAuth callback for a provider."""
        provider = await self.repo.get_by_id(provider_id)
        if provider is None:
            return f"Provider not found: {provider_id}"

        if not provider.enabled:
            return AuthResult(success=False, error="Provider is disabled")

        provider_cls = get_provider_class(provider.type)
        if provider_cls is None:
            return AuthResult(success=False, error=f"Unknown provider type: {provider.type}")

        instance = provider_cls(provider.config or {})
        result = await instance.handle_callback(code, state, redirect_uri)

        if result.success and result.claims:
            result.claims = self._apply_claim_mapping(result.claims, provider.claim_mapping or {})

        return result

    def _apply_claim_mapping(self, claims: Any, mapping: dict) -> Any:
        """Apply declarative claim mapping from provider config to claims.

        Mapping format: {"local_field": "external_claim_name", ...}
        e.g. {"username": "uid", "email": "mail", "displayName": "cn"}
        """
        if not mapping or not claims.raw_claims:
            return claims

        raw = claims.raw_claims
        if "username" in mapping and mapping["username"] in raw:
            claims.username = str(raw[mapping["username"]])
        if "email" in mapping and mapping["email"] in raw:
            claims.email = str(raw[mapping["email"]])
        if "displayName" in mapping and mapping["displayName"] in raw:
            claims.display_name = str(raw[mapping["displayName"]])

        return claims


def get_auth_provider_service(session: AsyncSession = Depends(get_db)) -> AuthProviderService:
    return AuthProviderService(session)
