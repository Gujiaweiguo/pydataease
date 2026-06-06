"""CLI module to initialize the admin user.

Runnable as: python -m app.commands.init_admin

Reads ``DE_ADMIN_PASSWORD`` from the environment, connects to the database,
and creates the admin user if it does not already exist.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.models.user import CoreUser
from app.settings.config import get_settings
from app.utils.password_utils import hash_password


async def _init_admin(password: str) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with session_factory() as session:
            stmt = select(CoreUser).where(CoreUser.account == "admin").limit(1)
            result = await session.execute(stmt)
            existing = result.scalars().first()

            if existing is not None:
                print("admin user already exists, skipping")
                return

            now_ns = time.time_ns()
            admin = CoreUser(
                id=1,
                account="admin",
                name="Administrator",
                password=hash_password(password),
                oid=1,
                enable=True,
                origin=0,
                mfa_enable=False,
                language="zh-CN",
                create_time=now_ns,
                update_time=now_ns,
            )
            session.add(admin)
            await session.commit()
            print("admin user created successfully")
    finally:
        await engine.dispose()


def main() -> None:
    password = os.environ.get("DE_ADMIN_PASSWORD", "").strip()
    if not password:
        print("Error: DE_ADMIN_PASSWORD environment variable is required", file=sys.stderr)
        sys.exit(1)

    asyncio.run(_init_admin(password))


if __name__ == "__main__":
    main()
