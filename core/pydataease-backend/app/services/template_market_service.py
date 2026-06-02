from __future__ import annotations

from typing import final

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.template import (
    VisualizationTemplate,
    VisualizationTemplateCategory,
    VisualizationTemplateCategoryMap,
)


@final
class TemplateMarketService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _fetch_templates(
        self, *, limit: int | None = None
    ) -> list[VisualizationTemplate]:
        """Fetch template leaf nodes ordered by create_time desc."""
        stmt = (
            select(VisualizationTemplate)
            .where(VisualizationTemplate.node_type == "template")
            .order_by(VisualizationTemplate.create_time.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _build_category_map(self) -> dict[str, list[str]]:
        """Return {template_id: [category_name, ...]}."""
        maps = (await self.session.execute(select(VisualizationTemplateCategoryMap))).scalars().all()
        if not maps:
            return {}
        cat_ids: set[str] = set()
        for m in maps:
            if m.category_id:
                cat_ids.add(m.category_id)
        if not cat_ids:
            return {m.template_id or "": [] for m in maps}
        cats = (await self.session.execute(
            select(VisualizationTemplateCategory).where(
                VisualizationTemplateCategory.id.in_(cat_ids)
            )
        )).scalars().all()
        cat_name: dict[str, str] = {c.id: (c.name or "") for c in cats}
        result: dict[str, list[str]] = {}
        for m in maps:
            tid = m.template_id or ""
            cid = m.category_id or ""
            result.setdefault(tid, []).append(cat_name.get(cid, ""))
        return result

    async def _fetch_categories_with_templates(
        self,
    ) -> list[VisualizationTemplateCategory]:
        """Fetch categories that have at least one template mapped."""
        subq = (
            select(VisualizationTemplateCategoryMap.category_id)
            .distinct()
        )
        stmt = select(VisualizationTemplateCategory).where(
            VisualizationTemplateCategory.id.in_(subq)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def _to_content_item(
        self,
        t: VisualizationTemplate,
        category_names: list[str],
    ) -> dict[str, object]:
        snapshot = t.snapshot or ""
        # Snapshots are either data-URLs, HTTP URLs, static-resource
        # paths, or raw base64 — all used directly without baseUrl prefix.
        thumbnail = snapshot
        return {
            "id": t.id,
            "title": t.name or "",
            "thumbnail": thumbnail,
            "templateType": t.dv_type or "PANEL",
            "source": "manage",
            "classify": "推荐",
            "categoryNames": category_names,
            "metas": {"theme_repo": ""},
        }

    # ------------------------------------------------------------------
    # Public API — consumed by routers/bootstrap.py
    # ------------------------------------------------------------------

    async def search_recommend(self) -> dict[str, object]:
        templates = await self._fetch_templates(limit=8)
        cat_map = await self._build_category_map()
        contents = [
            self._to_content_item(t, cat_map.get(t.id, []))
            for t in templates
        ]
        return {
            "baseUrl": "",
            "contents": contents,
        }

    async def search(self) -> dict[str, object]:
        templates = await self._fetch_templates()
        cat_map = await self._build_category_map()
        contents = [
            self._to_content_item(t, cat_map.get(t.id, []))
            for t in templates
        ]
        categories = await self._fetch_categories_with_templates()
        category_items = [
            {
                "label": c.name or "",
                "value": c.id,
                "source": "manage",
            }
            for c in categories
        ]
        return {
            "baseUrl": "",
            "categories": category_items,
            "contents": contents,
        }

    async def search_preview(self) -> dict[str, object]:
        return await self.search()

    async def get_categories(self) -> list[str]:
        categories = await self._fetch_categories_with_templates()
        return [c.name or "" for c in categories]

    async def get_categories_object(self) -> list[dict[str, str]]:
        fixed: list[dict[str, str]] = [
            {"value": "recent", "label": "最近", "source": "public"},
            {"value": "suggest", "label": "推荐", "source": "public"},
        ]
        categories = await self._fetch_categories_with_templates()
        for c in categories:
            fixed.append({
                "value": c.id,
                "label": c.name or "",
                "source": "manage",
            })
        return fixed


async def get_template_market_service(session: AsyncSession = Depends(get_db)) -> TemplateMarketService:
    return TemplateMarketService(session)
