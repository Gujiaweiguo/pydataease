from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_auth_link import UserAuthLink


class UserAuthLinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_provider_and_external_id(self, provider_id: int, external_id: str) -> UserAuthLink | None:
        stmt = select(UserAuthLink).where(
            UserAuthLink.provider_id == provider_id,
            UserAuthLink.external_id == external_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_provider(self, user_id: int, provider_id: int) -> UserAuthLink | None:
        stmt = select(UserAuthLink).where(
            UserAuthLink.user_id == user_id,
            UserAuthLink.provider_id == provider_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[UserAuthLink]:
        stmt = select(UserAuthLink).where(UserAuthLink.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: dict) -> UserAuthLink:
        link = UserAuthLink(**data)
        self.session.add(link)
        await self.session.flush()
        return link

    async def update(self, link: UserAuthLink, data: dict) -> UserAuthLink:
        for key, value in data.items():
            setattr(link, key, value)
        await self.session.flush()
        return link
