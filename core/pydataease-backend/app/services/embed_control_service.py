from __future__ import annotations

import logging
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.embed_config_repo import EmbedConfigRepository
from app.settings.defaults import is_feature_enabled

logger = logging.getLogger(__name__)

VALID_RESOURCE_TYPES = {"dashboard", "chart", "datav", "dataFiling"}


class EmbedControlService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = EmbedConfigRepository(session)

    # --- List / Query ---

    async def list_configs(self) -> list[dict[str, Any]]:
        configs = await self.repo.get_all()
        return [self._to_dict(c) for c in configs]

    async def get_config(self, resource_type: str) -> dict[str, Any] | None:
        config = await self.repo.get_by_resource_type(resource_type)
        if config is None:
            return None
        return self._to_dict(config)

    # --- Update ---

    async def update_config(self, resource_type: str, payload: dict[str, Any]) -> dict[str, Any] | str:
        if resource_type not in VALID_RESOURCE_TYPES:
            return f"Invalid resource type: {resource_type}"

        feature_on = await is_feature_enabled(self.session, "feature.embedding.enabled")
        if not feature_on:
            return "Embedding feature is disabled"

        updates: dict[str, Any] = {}
        if "embedEnabled" in payload:
            updates["embed_enabled"] = payload["embedEnabled"]
        if "allowedDomains" in payload:
            updates["allowed_domains"] = payload["allowedDomains"]
        if "passwordRequired" in payload:
            updates["password_required"] = payload["passwordRequired"]
        if "ticketRequired" in payload:
            updates["ticket_required"] = payload["ticketRequired"]
        if "maxExpiryHours" in payload:
            updates["max_expiry_hours"] = payload["maxExpiryHours"]
        if "extraConfig" in payload:
            updates["extra_config"] = payload["extraConfig"]

        config = await self.repo.upsert(resource_type, **updates)
        return self._to_dict(config)

    # --- Check ---

    async def is_embed_allowed(self, resource_type: str, domain: str | None = None) -> bool:
        feature_on = await is_feature_enabled(self.session, "feature.embedding.enabled")
        if not feature_on:
            return False

        config = await self.repo.get_by_resource_type(resource_type)
        if config is None or not config.embed_enabled:
            return False

        if domain is not None:
            return self._check_domain(config, domain)
        return True

    async def validate_domain(self, resource_type: str, domain: str) -> bool:
        config = await self.repo.get_by_resource_type(resource_type)
        if config is None:
            return False
        return self._check_domain(config, domain)

    # --- Internal ---

    def _check_domain(self, config: Any, domain: str) -> bool:
        allowed = config.allowed_domains
        if not allowed:
            return True
        return domain in allowed

    @staticmethod
    def _to_dict(config: Any) -> dict[str, Any]:
        return {
            "id": config.id,
            "resourceType": config.resource_type,
            "embedEnabled": config.embed_enabled,
            "allowedDomains": config.allowed_domains or [],
            "passwordRequired": config.password_required,
            "ticketRequired": config.ticket_required,
            "maxExpiryHours": config.max_expiry_hours,
            "extraConfig": config.extra_config or {},
            "createTime": str(config.create_time) if config.create_time else None,
            "updateTime": str(config.update_time) if config.update_time else None,
        }


def get_embed_control_service(session: AsyncSession = Depends(get_db)) -> EmbedControlService:
    return EmbedControlService(session)
