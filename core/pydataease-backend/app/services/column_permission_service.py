from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.column_permission import CoreColumnPermission
from app.schemas.auth import TokenUser
from app.schemas.column_permission import (
    ColumnPermissionCreateRequest,
    ColumnPermissionListRequest,
    ColumnPermissionResponse,
    ColumnPermissionUpdateRequest,
)
from app.services.permission_service import PermissionService


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


_VALID_ACTIONS = {"disable", "desensitize", "mask"}


@final
class ColumnPermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_rules(
        self, payload: ColumnPermissionListRequest, user: TokenUser
    ) -> list[ColumnPermissionResponse]:
        await self._require_manage(user, payload.dataset_id)
        stmt = select(CoreColumnPermission).where(
            CoreColumnPermission.dataset_id == payload.dataset_id
        ).order_by(CoreColumnPermission.id)
        result = await self.session.execute(stmt)
        return [ColumnPermissionResponse.model_validate(r) for r in result.scalars().all()]

    async def create_rule(
        self, payload: ColumnPermissionCreateRequest, user: TokenUser
    ) -> ColumnPermissionResponse:
        await self._require_manage(user, payload.dataset_id)
        if payload.action not in _VALID_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {payload.action}. Must be one of: {', '.join(sorted(_VALID_ACTIONS))}",
            )
        now = _timestamp_ms()
        rule = CoreColumnPermission(
            id=time.time_ns(),
            dataset_id=payload.dataset_id,
            field_id=payload.field_id,
            target_type=payload.target_type,
            target_id=payload.target_id,
            action=payload.action,
            enabled=payload.enabled,
            create_time=now,
            update_time=now,
        )
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return ColumnPermissionResponse.model_validate(rule)

    async def update_rule(
        self, payload: ColumnPermissionUpdateRequest, user: TokenUser
    ) -> ColumnPermissionResponse:
        rule = await self._get_rule(payload.id)
        await self._require_manage(user, rule.dataset_id)
        if payload.action is not None:
            if payload.action not in _VALID_ACTIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid action: {payload.action}. Must be one of: {', '.join(sorted(_VALID_ACTIONS))}",
                )
            rule.action = payload.action
        if payload.enabled is not None:
            rule.enabled = payload.enabled
        rule.update_time = _timestamp_ms()
        await self.session.commit()
        await self.session.refresh(rule)
        return ColumnPermissionResponse.model_validate(rule)

    async def delete_rule(self, rule_id: int, user: TokenUser) -> None:
        rule = await self._get_rule(rule_id)
        await self._require_manage(user, rule.dataset_id)
        await self.session.delete(rule)
        await self.session.commit()

    async def _get_rule(self, rule_id: int) -> CoreColumnPermission:
        stmt = select(CoreColumnPermission).where(CoreColumnPermission.id == rule_id)
        result = await self.session.execute(stmt)
        rule = result.scalar_one_or_none()
        if rule is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column permission rule not found")
        return rule

    async def _require_manage(self, user: TokenUser, dataset_id: int) -> None:
        if user.user_id == 1:
            return
        perm_service = PermissionService(self.session)
        has = await perm_service.has_resource_permission(user, "dataset", "manage")
        if not has:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manage permission required on dataset")


async def get_column_permission_service(session: AsyncSession = Depends(get_db)) -> ColumnPermissionService:
    return ColumnPermissionService(session=session)
