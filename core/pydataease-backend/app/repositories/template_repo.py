from __future__ import annotations

from typing import final

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import (
    VisualizationTemplate,
    VisualizationTemplateCategory,
    VisualizationTemplateCategoryMap,
)
from app.repositories.base import AsyncBaseRepository


@final
class TemplateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, VisualizationTemplate)
        self.session = session

    async def get_by_id(self, template_id: str) -> VisualizationTemplate | None:
        return await self.session.get(VisualizationTemplate, template_id)

    async def list_by_pid(self, pid: str) -> list[VisualizationTemplate]:
        stmt = select(VisualizationTemplate).where(VisualizationTemplate.pid == pid)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self) -> list[VisualizationTemplate]:
        stmt = select(VisualizationTemplate)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_node_type(self, node_type: str) -> list[VisualizationTemplate]:
        stmt = select(VisualizationTemplate).where(
            VisualizationTemplate.node_type == node_type
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_keyword(self, keyword: str) -> list[VisualizationTemplate]:
        stmt = select(VisualizationTemplate).where(
            VisualizationTemplate.name.ilike(f"%{keyword}%")
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, payload: dict[str, object]) -> VisualizationTemplate:
        return await self._base.create(payload)

    async def update(
        self, entity: VisualizationTemplate, payload: dict[str, object]
    ) -> VisualizationTemplate:
        return await self._base.update(entity, payload)

    async def delete(self, entity: VisualizationTemplate) -> None:
        await self._base.delete(entity)


@final
class TemplateCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, VisualizationTemplateCategory)
        self.session = session

    async def get_by_id(self, category_id: str) -> VisualizationTemplateCategory | None:
        return await self.session.get(VisualizationTemplateCategory, category_id)

    async def list_all(self) -> list[VisualizationTemplateCategory]:
        stmt = select(VisualizationTemplateCategory)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, payload: dict[str, object]) -> VisualizationTemplateCategory:
        return await self._base.create(payload)

    async def delete(self, entity: VisualizationTemplateCategory) -> None:
        await self._base.delete(entity)


@final
class TemplateCategoryMapRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, VisualizationTemplateCategoryMap)
        self.session = session

    async def list_by_template_id(
        self, template_id: str
    ) -> list[VisualizationTemplateCategoryMap]:
        stmt = select(VisualizationTemplateCategoryMap).where(
            VisualizationTemplateCategoryMap.template_id == template_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_category_id(
        self, category_id: str
    ) -> list[VisualizationTemplateCategoryMap]:
        stmt = select(VisualizationTemplateCategoryMap).where(
            VisualizationTemplateCategoryMap.category_id == category_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self, payload: dict[str, object]
    ) -> VisualizationTemplateCategoryMap:
        return await self._base.create(payload)

    async def delete_by_template_id(self, template_id: str) -> None:
        stmt = delete(VisualizationTemplateCategoryMap).where(
            VisualizationTemplateCategoryMap.template_id == template_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
