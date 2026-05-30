from __future__ import annotations

# pyright: reportMissingImports=false

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.config import get_settings  # pyright: ignore[reportImplicitRelativeImport]

from .defaults import SETTINGS_DEFAULTS


def _setting_type_for_key(key: str) -> str:
    return key.split(".", 1)[0]


async def seed_defaults() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with session_factory() as session:
            repo = SysSettingRepository(session)
            for key, value in SETTINGS_DEFAULTS.items():
                existing = await repo.get_by_key(key)
                if existing is None:
                    await repo.upsert(key, value, _setting_type_for_key(key))
    finally:
        await engine.dispose()
