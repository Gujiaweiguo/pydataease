from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_provider import AuthProvider


class AuthProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, provider_id: int) -> AuthProvider | None:
        stmt = select(AuthProvider).where(AuthProvider.id == provider_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, enabled_only: bool = False) -> list[AuthProvider]:
        stmt = select(AuthProvider).order_by(AuthProvider.create_time.desc())
        if enabled_only:
            stmt = stmt.where(AuthProvider.enabled == True)  # noqa: E712
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_type(self, provider_type: str) -> list[AuthProvider]:
        stmt = select(AuthProvider).where(AuthProvider.type == provider_type).order_by(AuthProvider.create_time.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_default(self) -> AuthProvider | None:
        stmt = select(AuthProvider).where(AuthProvider.is_default == True).limit(1)  # noqa: E712
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, provider: AuthProvider) -> AuthProvider:
        self.session.add(provider)
        await self.session.commit()
        await self.session.refresh(provider)
        return provider

    async def update(self, provider_id: int, **kwargs) -> AuthProvider | None:
        provider = await self.get_by_id(provider_id)
        if provider is None:
            return None
        for key, value in kwargs.items():
            if hasattr(provider, key):
                setattr(provider, key, value)
        await self.session.commit()
        await self.session.refresh(provider)
        return provider

    async def delete(self, provider_id: int) -> bool:
        provider = await self.get_by_id(provider_id)
        if provider is None:
            return False
        await self.session.delete(provider)
        await self.session.commit()
        return True

    async def clear_all_defaults(self) -> None:
        """Unset is_default on all providers."""
        stmt = update(AuthProvider).where(AuthProvider.is_default == True).values(is_default=False)  # noqa: E712
        await self.session.execute(stmt)
        # Don't commit here — caller will commit after setting new default
