from __future__ import annotations

from typing import final

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log import CoreLogOperate


@final
class LogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_paginated(
        self,
        page: int,
        page_size: int,
        keyword: str | None = None,
        op: str | None = None,
        uid: int | None = None,
        oid: int | None = None,
    ) -> tuple[list[CoreLogOperate], int]:
        """Returns (rows, total_count) with filtering and pagination."""
        stmt = select(CoreLogOperate)
        count_stmt = select(func.count()).select_from(CoreLogOperate)

        if keyword:
            filter_cond = or_(
                CoreLogOperate.name.ilike(f"%{keyword}%"),
                CoreLogOperate.op_text.ilike(f"%{keyword}%"),
            )
            stmt = stmt.where(filter_cond)
            count_stmt = count_stmt.where(filter_cond)
        if op:
            stmt = stmt.where(CoreLogOperate.op == op)
            count_stmt = count_stmt.where(CoreLogOperate.op == op)
        if uid:
            stmt = stmt.where(CoreLogOperate.uid == uid)
            count_stmt = count_stmt.where(CoreLogOperate.uid == uid)
        if oid:
            stmt = stmt.where(CoreLogOperate.oid == oid)
            count_stmt = count_stmt.where(CoreLogOperate.oid == oid)

        total = (await self.session.execute(count_stmt)).scalar() or 0
        stmt = (
            stmt.order_by(CoreLogOperate.time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total
