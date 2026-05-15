from __future__ import annotations

import time
from typing import final

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.share import CoreShareTicket, XpackShare
from app.repositories.base import AsyncBaseRepository


@final
class ShareRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, XpackShare)
        self.session = session

    async def get_by_resource_id(self, resource_id: int) -> XpackShare | None:
        stmt = select(XpackShare).where(XpackShare.resource_id == resource_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_uuid(self, uuid: str) -> XpackShare | None:
        stmt = select(XpackShare).where(XpackShare.uuid == uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, share_id: int) -> XpackShare | None:
        return await self._base.get_by_id(share_id)

    async def create(self, payload: dict[str, object]) -> XpackShare:
        return await self._base.create(payload)

    async def update(self, entity: XpackShare, payload: dict[str, object]) -> XpackShare:
        return await self._base.update(entity, payload)

    async def delete(self, entity: XpackShare) -> None:
        await self._base.delete(entity)

    async def delete_expired(self, exp_before: int) -> int:
        stmt = delete(XpackShare).where(
            XpackShare.exp.isnot(None),
            XpackShare.exp < exp_before,
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount


@final
class ShareTicketRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, CoreShareTicket)
        self.session = session

    async def list_by_uuid(self, uuid: str) -> list[CoreShareTicket]:
        stmt = select(CoreShareTicket).where(CoreShareTicket.uuid == uuid)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_ticket(self, ticket: str) -> CoreShareTicket | None:
        stmt = select(CoreShareTicket).where(CoreShareTicket.ticket == ticket)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, ticket_id: int) -> CoreShareTicket | None:
        return await self._base.get_by_id(ticket_id)

    async def create(self, payload: dict[str, object]) -> CoreShareTicket:
        return await self._base.create(payload)

    async def update(self, entity: CoreShareTicket, payload: dict[str, object]) -> CoreShareTicket:
        return await self._base.update(entity, payload)

    async def delete(self, entity: CoreShareTicket) -> None:
        await self._base.delete(entity)

    async def update_access_time(self, ticket_id: int) -> None:
        ticket = await self._base.get_by_id(ticket_id)
        if ticket is not None:
            await self._base.update(ticket, {"access_time": int(time.time() * 1000)})
