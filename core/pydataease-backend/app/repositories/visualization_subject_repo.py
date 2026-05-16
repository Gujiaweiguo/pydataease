from __future__ import annotations

from typing import final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visualization_subject import VisualizationSubject
from app.repositories.base import AsyncBaseRepository


@final
class VisualizationSubjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, VisualizationSubject)
        self.session = session

    async def list_active(self) -> list[VisualizationSubject]:
        stmt = select(VisualizationSubject).where(
            VisualizationSubject.delete_flag == False  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, subject_id: str) -> VisualizationSubject | None:
        return await self.session.get(VisualizationSubject, subject_id)

    async def get_by_name(self, name: str) -> VisualizationSubject | None:
        stmt = select(VisualizationSubject).where(VisualizationSubject.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, payload: dict) -> VisualizationSubject:
        return await self._base.create(payload)

    async def update(
        self, entity: VisualizationSubject, payload: dict
    ) -> VisualizationSubject:
        return await self._base.update(entity, payload)

    async def delete(self, entity: VisualizationSubject) -> None:
        await self._base.delete(entity)
