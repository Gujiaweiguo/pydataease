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
from app.schemas.user import (
    DefaultPasswordResponse,
    UserByCurrentOrgRequest,
    UserCreateRequest,
    UserDetailResponse,
    UserEditRequest,
    UserEnableRequest,
    UserListItemResponse,
    UserOrgMembershipResponse,
    UserPagerRequest,
    UserPagerResponse,
    UserRoleSelectedRequest,
    UserRoleResponse,
)
from app.utils.password_utils import hash_password

DEFAULT_PASSWORD = "DataEase@123456"
SYSTEM_ADMIN_ROLE_ID = 1


@final
class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.org_repo = OrgRepository(session)

    async def pager(self, page: int, limit: int, payload: UserPagerRequest | None, user: TokenUser) -> UserPagerResponse:
        normalized_page = max(page, 1)
        normalized_limit = max(limit, 1)
        users, total = await self.user_repo.search(
            keyword=payload.keyword if payload else None,
            enable=payload.enable if payload else None,
            oid=None if user.user_id == 1 else user.oid,
            offset=(normalized_page - 1) * normalized_limit,
            limit=normalized_limit,
        )
        return UserPagerResponse(items=await self._build_user_items(users), total=total)

    async def create(self, payload: UserCreateRequest, user: TokenUser) -> UserDetailResponse:
        target_oid = self._resolve_target_oid(payload.oid, user)
        if await self.user_repo.get_by_account(payload.account.strip()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already exists")
        if target_oid and user.user_id != 1 and not await self.org_repo.is_member(user.user_id, target_oid):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot manage users outside current organization")

        await self._validate_role_ids(payload.role_ids, target_oid)
        now = _timestamp_ms()
        created = await self.user_repo.create(
            {
                "id": _new_identifier(),
                "account": payload.account.strip(),
                "name": payload.name.strip(),
                "email": _clean_optional(payload.email),
                "phone": _clean_optional(payload.phone),
                "phone_prefix": None,
                "password": hash_password(DEFAULT_PASSWORD),
                "enable": True,
                "oid": target_oid,
                "origin": 0,
                "mfa_enable": False,
                "language": "zh-CN",
                "create_time": now,
                "update_time": now,
            }
        )
        await self._ensure_user_org_membership(created.id, target_oid)
        if payload.role_ids:
            await self._replace_role_bindings(created.id, target_oid, payload.role_ids)
        return await self.query_by_id(created.id, user)

    async def edit(self, payload: UserEditRequest, user: TokenUser) -> UserDetailResponse:
        entity = await self._get_manageable_user(payload.id, user)
        update_data: dict[str, object] = {
            "update_time": _timestamp_ms(),
        }
        if payload.name is not None:
            update_data["name"] = payload.name.strip()
        if payload.email is not None:
            update_data["email"] = _clean_optional(payload.email)
        if payload.phone is not None:
            update_data["phone"] = _clean_optional(payload.phone)
        await self.user_repo.update(entity, update_data)
        if payload.role_ids is not None:
            await self._validate_role_ids(payload.role_ids, user.oid)
            await self._replace_role_bindings(entity.id, user.oid, payload.role_ids)
        return await self.query_by_id(entity.id, user)

    async def delete(self, uid: int, user: TokenUser) -> None:
        if uid == 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="System administrator cannot be deleted")
        entity = await self._get_manageable_user(uid, user)
        await self._ensure_not_last_admin(uid)
        await self.session.execute(delete(CoreRoleUser).where(CoreRoleUser.user_id == uid))
        await self.session.execute(delete(CoreUserOrg).where(CoreUserOrg.user_id == uid))
        await self.session.commit()
        await self.user_repo.delete(entity)

    async def enable(self, payload: UserEnableRequest, user: TokenUser) -> None:
        entity = await self._get_manageable_user(payload.id, user)
        if not payload.enable:
            await self._ensure_not_last_admin(entity.id)
        await self.user_repo.update(entity, {"enable": payload.enable, "update_time": _timestamp_ms()})

    async def reset_password(self, uid: int, user: TokenUser) -> None:
        entity = await self._get_manageable_user(uid, user)
        await self.user_repo.update(entity, {"password": hash_password(DEFAULT_PASSWORD), "update_time": _timestamp_ms()})

    async def query_by_id(self, uid: int, user: TokenUser) -> UserDetailResponse:
        entity = await self._get_manageable_user(uid, user)
        orgs = await self.org_repo.get_user_orgs(entity.id)
        roles = await self._get_user_roles(entity.id, user.oid, user.user_id == 1)
        return UserDetailResponse(
            id=entity.id,
            account=entity.account,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            enable=entity.enable,
            oid=entity.oid,
            role_ids=[role.id for role in roles],
            roles=[UserRoleResponse.model_validate(role) for role in roles],
            org_ids=[org.id for org in orgs],
            orgs=[UserOrgMembershipResponse.model_validate(org) for org in orgs],
            create_time=entity.create_time,
            update_time=entity.update_time,
        )

    async def default_password(self) -> DefaultPasswordResponse:
        return DefaultPasswordResponse(password=DEFAULT_PASSWORD)

    async def users_in_role(
        self,
        page: int,
        limit: int,
        payload: UserRoleSelectedRequest,
        user: TokenUser,
    ) -> UserPagerResponse:
        normalized_page = max(page, 1)
        normalized_limit = max(limit, 1)
        _ = await self._get_role_in_scope(payload.role_id, user)
        stmt = (
            select(CoreUser)
            .join(CoreRoleUser, CoreRoleUser.user_id == CoreUser.id)
            .where(CoreRoleUser.role_id == payload.role_id, CoreRoleUser.oid == user.oid)
            .order_by(CoreUser.id)
            .offset((normalized_page - 1) * normalized_limit)
            .limit(normalized_limit)
        )
        count_stmt = (
            select(func.count(func.distinct(CoreUser.id)))
            .select_from(CoreUser)
            .join(CoreRoleUser, CoreRoleUser.user_id == CoreUser.id)
            .where(CoreRoleUser.role_id == payload.role_id, CoreRoleUser.oid == user.oid)
        )
        result = await self.session.execute(stmt)
        total_result = await self.session.execute(count_stmt)
        users = list(result.scalars().all())
        return UserPagerResponse(items=await self._build_user_items(users), total=int(total_result.scalar_one()))

    async def by_current_org(
        self,
        payload: UserByCurrentOrgRequest | None,
        user: TokenUser,
    ) -> list[UserListItemResponse]:
        users = await (self.user_repo.list_all() if user.user_id == 1 else self.org_repo.get_org_users(user.oid))
        keyword = payload.keyword.strip() if payload and payload.keyword else ""
        if keyword:
            lowered = keyword.lower()
            users = [candidate for candidate in users if self._matches_keyword(candidate, lowered)]
        return await self._build_user_items(users)

    async def _build_user_items(self, users: list[CoreUser]) -> list[UserListItemResponse]:
        if not users:
            return []
        user_ids = [user.id for user in users]
        role_map = await self._get_user_role_ids(user_ids)
        org_map = await self._get_user_org_ids(user_ids)
        return [
            UserListItemResponse(
                id=item.id,
                account=item.account,
                name=item.name,
                email=item.email,
                phone=item.phone,
                enable=item.enable,
                oid=item.oid,
                create_time=item.create_time,
                update_time=item.update_time,
                role_ids=role_map.get(item.id, []),
                org_ids=org_map.get(item.id, []),
            )
            for item in users
        ]

    async def _get_manageable_user(self, uid: int, user: TokenUser) -> CoreUser:
        entity = await self.user_repo.get_by_id(uid)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.user_id != 1 and not await self.org_repo.is_member(uid, user.oid):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return entity

    async def _get_role_in_scope(self, role_id: int, user: TokenUser) -> CoreRole:
        role = await self.role_repo.get_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        if user.user_id != 1 and role.oid not in (0, user.oid):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role

    async def _validate_role_ids(self, role_ids: list[int] | None, oid: int) -> None:
        if not role_ids:
            return
        unique_role_ids = list(dict.fromkeys(role_ids))
        stmt = select(CoreRole.id).where(CoreRole.id.in_(unique_role_ids), or_(CoreRole.oid == 0, CoreRole.oid == oid))
        result = await self.session.execute(stmt)
        found_ids = set(result.scalars().all())
        if len(found_ids) != len(unique_role_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more roles are invalid")

    async def _replace_role_bindings(self, user_id: int, oid: int, role_ids: list[int]) -> None:
        await self.session.execute(delete(CoreRoleUser).where(CoreRoleUser.user_id == user_id, CoreRoleUser.oid == oid))
        unique_role_ids = list(dict.fromkeys(role_ids))
        for role_id in unique_role_ids:
            self.session.add(CoreRoleUser(id=_new_identifier(), role_id=role_id, user_id=user_id, oid=oid))
        await self.session.commit()

    async def _ensure_user_org_membership(self, user_id: int, oid: int) -> None:
        if oid <= 0:
            return
        if await self.org_repo.get_by_id(oid) is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization not found")
        self.session.add(CoreUserOrg(id=_new_identifier(), user_id=user_id, org_id=oid))
        await self.session.commit()

    async def _ensure_not_last_admin(self, user_id: int) -> None:
        stmt = select(func.count()).select_from(CoreRoleUser).where(CoreRoleUser.role_id == SYSTEM_ADMIN_ROLE_ID)
        total_admins = int((await self.session.execute(stmt)).scalar_one())
        is_admin = await self.role_repo.is_user_in_role(user_id, SYSTEM_ADMIN_ROLE_ID, 0)
        if is_admin and total_admins <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot disable or delete the last administrator")

    async def _get_user_roles(self, user_id: int, oid: int, is_admin: bool) -> list[CoreRole]:
        stmt = select(CoreRole).join(CoreRoleUser, CoreRoleUser.role_id == CoreRole.id).where(CoreRoleUser.user_id == user_id)
        if not is_admin:
            stmt = stmt.where(CoreRoleUser.oid == oid)
        stmt = stmt.order_by(CoreRole.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _get_user_role_ids(self, user_ids: list[int]) -> dict[int, list[int]]:
        stmt = select(CoreRoleUser.user_id, CoreRoleUser.role_id).where(CoreRoleUser.user_id.in_(user_ids))
        result = await self.session.execute(stmt)
        payload: dict[int, list[int]] = {user_id: [] for user_id in user_ids}
        for user_id, role_id in result.all():
            payload.setdefault(user_id, []).append(role_id)
        return payload

    async def _get_user_org_ids(self, user_ids: list[int]) -> dict[int, list[int]]:
        stmt = select(CoreUserOrg.user_id, CoreUserOrg.org_id).where(CoreUserOrg.user_id.in_(user_ids))
        result = await self.session.execute(stmt)
        payload: dict[int, list[int]] = {user_id: [] for user_id in user_ids}
        for user_id, org_id in result.all():
            payload.setdefault(user_id, []).append(org_id)
        return payload

    @staticmethod
    def _resolve_target_oid(payload_oid: int | None, user: TokenUser) -> int:
        if payload_oid is not None:
            if user.user_id != 1 and payload_oid != user.oid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create user outside current organization")
            return payload_oid
        return user.oid

    @staticmethod
    def _matches_keyword(user: CoreUser, keyword: str) -> bool:
        return any(
            keyword in (value or "").lower()
            for value in (user.account, user.name, user.email, user.phone)
        )


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session=session)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
