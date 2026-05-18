from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class AsyncBaseRepository(Generic[ModelT]):
    session: AsyncSession
    model: type[ModelT]
    _writable_fields: set[str] | None = None  # None means allow all

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def _filter_payload(self, payload: dict[str, object]) -> dict[str, object]:
        if self._writable_fields is None:
            return payload
        return {k: v for k, v in payload.items() if k in self._writable_fields}

    async def get(self, statement: Select[tuple[ModelT]]) -> Sequence[ModelT]:
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def list(self) -> Sequence[ModelT]:
        return await self.get(select(self.model))

    async def get_by_id(self, entity_id: int) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def create(self, payload: dict[str, object]) -> ModelT:
        filtered = self._filter_payload(payload)
        entity = self.model(**filtered)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT, payload: dict[str, object]) -> ModelT:
        filtered = self._filter_payload(payload)
        for key, value in filtered.items():
            setattr(entity, key, value)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.commit()
