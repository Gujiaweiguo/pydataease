from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embed_config import EmbedConfig


class EmbedConfigRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_resource_type(self, resource_type: str) -> EmbedConfig | None:
        stmt = select(EmbedConfig).where(EmbedConfig.resource_type == resource_type).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> list[EmbedConfig]:
        stmt = select(EmbedConfig).order_by(EmbedConfig.resource_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(self, resource_type: str, **kwargs) -> EmbedConfig:
        existing = await self.get_by_resource_type(resource_type)
        if existing is not None:
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        config = EmbedConfig(resource_type=resource_type, **kwargs)
        self.session.add(config)
        await self.session.commit()
        await self.session.refresh(config)
        return config

    async def delete(self, resource_type: str) -> bool:
        config = await self.get_by_resource_type(resource_type)
        if config is None:
            return False
        await self.session.delete(config)
        await self.session.commit()
        return True
