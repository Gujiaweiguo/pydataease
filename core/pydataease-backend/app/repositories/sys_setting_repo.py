from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sys_setting import CoreSysSetting


@final
class SysSettingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_key(self, key: str) -> CoreSysSetting | None:
        stmt = select(CoreSysSetting).where(CoreSysSetting.setting_key == key).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_type(self, setting_type: str) -> Sequence[CoreSysSetting]:
        stmt = select(CoreSysSetting).where(CoreSysSetting.type == setting_type)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all(self) -> Sequence[CoreSysSetting]:
        stmt = select(CoreSysSetting).order_by(CoreSysSetting.id.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def upsert(self, key: str, value: str, setting_type: str = "setting") -> CoreSysSetting:
        existing = await self.get_by_key(key)
        if existing is not None:
            existing.setting_value = value
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        entity = CoreSysSetting(setting_key=key, setting_value=value, type=setting_type)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
