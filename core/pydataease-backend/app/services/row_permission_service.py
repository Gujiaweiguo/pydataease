from __future__ import annotations

import re
import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.permission_whitelist import CorePermissionWhitelist
from app.models.row_permission import CoreRowPermission
from app.schemas.auth import TokenUser
from app.schemas.row_permission import (
    RowPermissionCreateRequest,
    RowPermissionListRequest,
    RowPermissionResponse,
    RowPermissionUpdateRequest,
)
from app.services.permission_service import PermissionService

_DANGEROUS_SQL_RE = re.compile(
    r"\b(drop|delete|update|insert|alter|create|truncate|grant|revoke|exec|execute|merge|call)\b",
    re.IGNORECASE,
)


def _validate_filter_sql(filter_sql: str) -> None:
    """Validate that filter_sql does not contain dangerous statements."""
    if _DANGEROUS_SQL_RE.search(filter_sql):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="filter_sql contains forbidden SQL keywords",
        )


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


@final
class RowPermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_rules(
        self, payload: RowPermissionListRequest, user: TokenUser
    ) -> list[RowPermissionResponse]:
        await self._require_manage(user, payload.dataset_id)
        stmt = select(CoreRowPermission).where(
            CoreRowPermission.dataset_id == payload.dataset_id
        ).order_by(CoreRowPermission.id)
        result = await self.session.execute(stmt)
        return [RowPermissionResponse.model_validate(r) for r in result.scalars().all()]

    async def create_rule(
        self, payload: RowPermissionCreateRequest, user: TokenUser
    ) -> RowPermissionResponse:
        await self._require_manage(user, payload.dataset_id)
        _validate_filter_sql(payload.filter_sql)
        now = _timestamp_ms()
        rule = CoreRowPermission(
            id=time.time_ns(),
            dataset_id=payload.dataset_id,
            target_type=payload.target_type,
            target_id=payload.target_id,
            filter_sql=payload.filter_sql,
            enabled=payload.enabled,
            create_time=now,
            update_time=now,
        )
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return RowPermissionResponse.model_validate(rule)

    async def update_rule(
        self, payload: RowPermissionUpdateRequest, user: TokenUser
    ) -> RowPermissionResponse:
        rule = await self._get_rule(payload.id)
        await self._require_manage(user, rule.dataset_id)
        if payload.filter_sql is not None:
            _validate_filter_sql(payload.filter_sql)
            rule.filter_sql = payload.filter_sql
        if payload.enabled is not None:
            rule.enabled = payload.enabled
        rule.update_time = _timestamp_ms()
        await self.session.commit()
        await self.session.refresh(rule)
        return RowPermissionResponse.model_validate(rule)

    async def delete_rule(self, rule_id: int, user: TokenUser) -> None:
        rule = await self._get_rule(rule_id)
        await self._require_manage(user, rule.dataset_id)
        await self.session.delete(rule)
        await self.session.commit()

    async def list_whitelist(self, user: TokenUser) -> list[dict]:
        if user.user_id != 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
        stmt = select(CorePermissionWhitelist).order_by(CorePermissionWhitelist.id)
        result = await self.session.execute(stmt)
        entries = result.scalars().all()
        return [
            {
                "id": e.id,
                "user_id": e.user_id,
                "dataset_id": e.dataset_id,
                "scope": e.scope,
                "create_time": e.create_time,
            }
            for e in entries
        ]

    async def add_whitelist(
        self, user_id: int, dataset_id: int, scope: str, user: TokenUser
    ) -> dict:
        if user.user_id != 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
        now = _timestamp_ms()
        entry = CorePermissionWhitelist(
            id=time.time_ns(),
            user_id=user_id,
            dataset_id=dataset_id,
            scope=scope,
            create_time=now,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return {
            "id": entry.id,
            "user_id": entry.user_id,
            "dataset_id": entry.dataset_id,
            "scope": entry.scope,
            "create_time": entry.create_time,
        }

    async def remove_whitelist(self, whitelist_id: int, user: TokenUser) -> None:
        if user.user_id != 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
        stmt = select(CorePermissionWhitelist).where(CorePermissionWhitelist.id == whitelist_id)
        result = await self.session.execute(stmt)
        entry = result.scalar_one_or_none()
        if entry is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Whitelist entry not found")
        await self.session.delete(entry)
        await self.session.commit()

    async def _get_rule(self, rule_id: int) -> CoreRowPermission:
        stmt = select(CoreRowPermission).where(CoreRowPermission.id == rule_id)
        result = await self.session.execute(stmt)
        rule = result.scalar_one_or_none()
        if rule is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Row permission rule not found")
        return rule

    async def _require_manage(self, user: TokenUser, dataset_id: int) -> None:
        if user.user_id == 1:
            return
        perm_service = PermissionService(self.session)
        has = await perm_service.has_resource_permission(user, "dataset", "manage")
        if not has:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manage permission required on dataset")


async def get_row_permission_service(session: AsyncSession = Depends(get_db)) -> RowPermissionService:
    return RowPermissionService(session=session)
