from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.role import CoreRole
from app.models.role_user import CoreRoleUser
from app.models.user import CoreUser
from app.models.user_org import CoreUserOrg
from app.repositories.org_repo import OrgRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenUser
from app.schemas.role import (
    RoleBeforeUnmountRequest,
    RoleCreateRequest,
    RoleDetailResponse,
    RoleEditRequest,
    RoleMountExternalRequest,
    RoleMountRequest,
    RoleQueryRequest,
    RoleResponse,
    RoleUnmountRequest,
    RoleUserOptionRequest,
    RoleUserOptionResponse,
)


@final
class RoleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.role_repo = RoleRepository(session)
        self.org_repo = OrgRepository(session)
        self.user_repo = UserRepository(session)

    async def query(self, payload: RoleQueryRequest | None, user: TokenUser) -> list[RoleResponse]:
        roles = await self.role_repo.list_by_org(user.oid)
        keyword = payload.keyword.strip() if payload and payload.keyword else ""
        if keyword:
            lowered = keyword.lower()
            roles = [role for role in roles if lowered in role.name.lower()]
        return [RoleResponse.model_validate(role) for role in roles]

    async def create(self, payload: RoleCreateRequest, user: TokenUser) -> RoleResponse:
        self._require_current_org(user)
        await self._ensure_role_name_available(payload.name, user.oid, None)
        now = _timestamp_ms()
        role = await self.role_repo.create(
            {
                "id": _new_identifier(),
                "name": payload.name.strip(),
                "description": _clean_optional(payload.description),
                "oid": user.oid,
                "type": 1,
                "create_time": now,
                "update_time": now,
            }
        )
        return RoleResponse.model_validate(role)

    async def edit(self, payload: RoleEditRequest, user: TokenUser) -> RoleResponse:
        role = await self._get_manageable_role(payload.id, user)
        new_name = payload.name.strip() if payload.name is not None else role.name
        await self._ensure_role_name_available(new_name, role.oid, role.id)
        updated = await self.role_repo.update(
            role,
            {
                "name": new_name,
                "description": _clean_optional(payload.description) if payload.description is not None else role.description,
                "update_time": _timestamp_ms(),
            },
        )
        return RoleResponse.model_validate(updated)

    async def detail(self, rid: int, user: TokenUser) -> RoleDetailResponse:
        role = await self._get_visible_role(rid, user)
        member_count = len(await self.role_repo.get_role_users(role.id))
        return RoleDetailResponse.model_validate({
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "oid": role.oid,
            "type": role.type,
            "create_time": role.create_time,
            "update_time": role.update_time,
            "member_count": member_count,
        })

    async def delete(self, rid: int, user: TokenUser) -> None:
        role = await self._get_manageable_role(rid, user)
        await self.session.execute(delete(CoreRoleUser).where(CoreRoleUser.role_id == rid))
        await self.session.commit()
        await self.role_repo.delete(role)

    async def user_option(self, payload: RoleUserOptionRequest | None, user: TokenUser) -> list[RoleUserOptionResponse]:
        self._require_current_org(user)
        keyword = payload.keyword.strip() if payload and payload.keyword else ""
        stmt = (
            select(CoreUser)
            .join(CoreUserOrg, CoreUserOrg.user_id == CoreUser.id)
            .where(CoreUserOrg.org_id == user.oid)
            .order_by(CoreUser.id)
        )
        if keyword:
            like_value = f"%{keyword}%"
            stmt = stmt.where(or_(CoreUser.account.ilike(like_value), CoreUser.name.ilike(like_value)))
        result = await self.session.execute(stmt)
        return [RoleUserOptionResponse.model_validate(item) for item in result.scalars().all()]

    async def search_external_user(self, keyword: str, user: TokenUser) -> list[RoleUserOptionResponse]:
        self._require_current_org(user)
        cleaned_keyword = keyword.strip()
        if not cleaned_keyword:
            return []
        membership_subquery = select(CoreUserOrg.user_id).where(CoreUserOrg.org_id == user.oid)
        like_value = f"%{cleaned_keyword}%"
        stmt = (
            select(CoreUser)
            .where(~CoreUser.id.in_(membership_subquery))
            .where(or_(CoreUser.account.ilike(like_value), CoreUser.name.ilike(like_value)))
            .order_by(CoreUser.id)
            .limit(50)
        )
        result = await self.session.execute(stmt)
        return [RoleUserOptionResponse.model_validate(item) for item in result.scalars().all()]

    async def mount_user(self, payload: RoleMountRequest, user: TokenUser) -> None:
        self._require_current_org(user)
        role = await self._get_visible_role(payload.role_id, user)
        unique_user_ids = list(dict.fromkeys(payload.user_ids))
        for user_id in unique_user_ids:
            await self._get_bindable_user(user_id, user)
            if role.oid not in (0, user.oid):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role is not available in current organization")
            if not await self.role_repo.is_user_in_role(user_id, role.id, user.oid):
                await self.role_repo.bind_user(role.id, user_id, user.oid)

    async def unmount_user(self, payload: RoleUnmountRequest, user: TokenUser) -> None:
        self._require_current_org(user)
        role = await self._get_visible_role(payload.role_id, user)
        unique_user_ids = list(dict.fromkeys(payload.user_ids))
        for user_id in unique_user_ids:
            await self._get_bindable_user(user_id, user)
            await self.role_repo.unbind_user(role.id, user_id, user.oid)
        # Clean up orphaned users: if user has no remaining roles across any org, remove them
        for user_id in unique_user_ids:
            if user_id == 1:
                continue
            remaining = await self._count_user_roles(user_id)
            if remaining == 0:
                await self.session.execute(delete(CoreUserOrg).where(CoreUserOrg.user_id == user_id))
                await self.session.commit()
                user_entity = await self.user_repo.get_by_id(user_id)
                if user_entity is not None:
                    await self.user_repo.delete(user_entity)

    async def before_unmount_info(self, payload: RoleBeforeUnmountRequest, user: TokenUser) -> list[dict[str, object]]:
        await self._get_visible_role(payload.role_id, user)
        results = []
        for uid in payload.user_ids:
            target_user = await self.user_repo.get_by_id(uid)
            if target_user is None:
                continue
            stmt = select(func.count()).select_from(CoreRoleUser).where(
                CoreRoleUser.user_id == uid, CoreRoleUser.oid == user.oid
            )
            total_roles = int((await self.session.execute(stmt)).scalar_one())
            results.append(
                {
                    "id": target_user.id,
                    "name": target_user.name,
                    "account": target_user.account,
                    "remainingRoleCount": max(0, total_roles - 1),
                }
            )
        return results

    async def mount_external_user(self, payload: RoleMountExternalRequest, user: TokenUser) -> dict[str, object]:
        role = await self._get_visible_role(payload.role_id, user)
        mounted = []
        not_found = []
        for account in payload.accounts:
            target = await self.user_repo.get_by_account(account.strip())
            if target is None:
                not_found.append(account)
                continue
            existing = await self.session.execute(
                select(CoreRoleUser).where(
                    CoreRoleUser.role_id == role.id,
                    CoreRoleUser.user_id == target.id,
                    CoreRoleUser.oid == user.oid,
                )
            )
            if existing.scalar_one_or_none() is None:
                self.session.add(
                    CoreRoleUser(
                        id=time.time_ns(),
                        role_id=role.id,
                        user_id=target.id,
                        oid=user.oid,
                    )
                )
                await self.session.commit()
            mounted.append(account)
        return {"mounted": mounted, "notFound": not_found}

    async def by_org(self, payload: RoleQueryRequest | None, user: TokenUser) -> list[RoleResponse]:
        return await self.query(payload, user)

    async def _get_visible_role(self, rid: int, user: TokenUser) -> CoreRole:
        role = await self.role_repo.get_by_id(rid)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        if user.user_id != 1 and role.oid not in (0, user.oid):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role

    async def _get_manageable_role(self, rid: int, user: TokenUser) -> CoreRole:
        role = await self._get_visible_role(rid, user)
        if role.type == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Built-in roles cannot be modified")
        if user.user_id != 1 and role.oid != user.oid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot manage roles outside current organization")
        return role

    async def _ensure_role_name_available(self, name: str, oid: int, exclude_id: int | None) -> None:
        stmt = select(func.count()).select_from(CoreRole).where(CoreRole.oid == oid, CoreRole.name == name.strip())
        if exclude_id is not None:
            stmt = stmt.where(CoreRole.id != exclude_id)
        exists = int((await self.session.execute(stmt)).scalar_one())
        if exists > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")

    async def _get_bindable_user(self, user_id: int, current_user: TokenUser) -> CoreUser:
        entity = await self.user_repo.get_by_id(user_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if current_user.oid > 0 and not await self.org_repo.is_member(user_id, current_user.oid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not in current organization")
        return entity

    async def _count_user_roles(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(CoreRoleUser).where(CoreRoleUser.user_id == user_id)
        return int((await self.session.execute(stmt)).scalar_one())

    @staticmethod
    def _require_current_org(user: TokenUser) -> None:
        if user.oid <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current organization is required")


async def get_role_service(session: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(session=session)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
