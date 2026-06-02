from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.template import (
    VisualizationTemplate,
    VisualizationTemplateCategory,
    VisualizationTemplateCategoryMap,
)
from app.repositories.store_repo import StoreRepository
from app.repositories.template_repo import (
    TemplateCategoryMapRepository,
    TemplateCategoryRepository,
    TemplateRepository,
)
from app.schemas.auth import TokenUser
from app.schemas.template import (
    BatchDeleteRequest,
    BatchUpdateRequest,
    CategoryTemplateNameCheckRequest,
    FindCategoriesByTemplateIdsRequest,
    FindCategoriesRequest,
    NameCheckRequest,
    TemplateFindRequest,
    TemplateListBodyRequest,
    TemplateSaveRequest,
    TemplateTreeNode,
    TemplateUpdateRequest,
)


def _new_id() -> str:
    return str(time.time_ns())


def _build_tree(
    nodes: list[VisualizationTemplate | VisualizationTemplateCategory],
) -> list[TemplateTreeNode]:
    node_map: dict[str, TemplateTreeNode] = {}
    roots: list[TemplateTreeNode] = []

    for item in nodes:
        node = TemplateTreeNode.model_validate(item)
        node.children = []
        node_map[node.id] = node

    for node in node_map.values():
        pid = node.pid or "0"
        if pid == "0" or pid not in node_map:
            roots.append(node)
        else:
            node_map[pid].children.append(node)

    return roots


@final
class TemplateService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.template_repo = TemplateRepository(session)
        self.category_repo = TemplateCategoryRepository(session)
        self.category_map_repo = TemplateCategoryMapRepository(session)
        self.store_repo = StoreRepository(session)

    # ------------------------------------------------------------------
    # Template methods
    # ------------------------------------------------------------------

    async def tree(self) -> list[dict]:
        categories = await self.category_repo.list_all()
        cat_tree = _build_tree(categories)  # type: ignore[arg-type]
        for cat in cat_tree:
            await self._attach_templates_to_node(cat)
        return [n.model_dump(by_alias=True) for n in cat_tree]

    async def _attach_templates_to_node(self, node: TemplateTreeNode) -> None:
        maps = await self.category_map_repo.list_by_category_id(node.id)
        for m in maps:
            tpl = await self.template_repo.get_by_id(m.template_id)  # type: ignore[arg-type]
            if tpl is not None:
                child = TemplateTreeNode.model_validate(tpl)
                node.children.append(child)
        for child in node.children:
            if child.children:
                await self._attach_templates_to_node(child)

    async def save(
        self,
        payload: TemplateSaveRequest,
        user: TokenUser,
    ) -> dict:
        tpl_id = _new_id()
        data: dict[str, object] = {
            "id": tpl_id,
            "name": payload.name,
            "pid": payload.pid,
            "level": 0,
            "dv_type": payload.dv_type,
            "node_type": payload.node_type,
            "create_by": str(user.user_id),
            "create_time": int(time.time() * 1000),
            "snapshot": payload.snapshot,
            "template_type": payload.template_type,
            "template_style": payload.template_style,
            "template_data": payload.template_data,
            "dynamic_data": payload.dynamic_data,
        }
        tpl = await self.template_repo.create(data)
        return _tpl_to_dict(tpl)

    async def name_list(self) -> list[dict]:
        templates = await self.template_repo.list_all()
        return [{"id": t.id, "name": t.name} for t in templates]

    async def categories(self) -> list[dict]:
        categories = await self.category_repo.list_all()
        tree = _build_tree(categories)  # type: ignore[arg-type]
        return [n.model_dump(by_alias=True) for n in tree]

    async def find_categories(self, payload: FindCategoriesRequest) -> list[dict]:
        categories = await self.category_repo.list_all()
        if payload.dv_type:
            categories = [c for c in categories if c.dv_type == payload.dv_type]
        if payload.template_type:
            categories = [
                c for c in categories if c.template_type == payload.template_type
            ]
        tree = _build_tree(categories)  # type: ignore[arg-type]
        return [n.model_dump(by_alias=True) for n in tree]

    async def category_form(self, category_id: str) -> dict:
        cat = await self.category_repo.get_by_id(category_id)
        if cat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        maps = await self.category_map_repo.list_by_category_id(category_id)
        templates: list[dict] = []
        for m in maps:
            tpl = await self.template_repo.get_by_id(m.template_id)  # type: ignore[arg-type]
            if tpl is not None:
                templates.append(_tpl_to_dict(tpl))
        return {
            "category": _cat_to_dict(cat),
            "templates": templates,
        }

    async def delete(self, template_id: str, category_id: str | None = None) -> None:
        tpl = await self.template_repo.get_by_id(template_id)
        if tpl is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        if category_id:
            maps = await self.category_map_repo.list_by_category_id(category_id)
            for m in maps:
                if m.template_id == template_id:
                    await self.session.delete(m)
            remaining = await self.category_map_repo.list_by_template_id(template_id)
            if not remaining:
                await self.template_repo.delete(tpl)
        else:
            await self.category_map_repo.delete_by_template_id(template_id)
            await self.template_repo.delete(tpl)
        await self.session.commit()

    async def find_one(self, template_id: str) -> dict | None:
        tpl = await self.template_repo.get_by_id(template_id)
        if tpl is None:
            return None
        return _tpl_to_dict(tpl)

    async def find_by_body(self, payload: TemplateFindRequest) -> list[dict]:
        tid = payload.id or payload.template_id
        if tid:
            tpl = await self.template_repo.get_by_id(tid)
            if tpl is not None:
                return [_tpl_to_dict(tpl)]
            return []
        templates = await self.template_repo.list_all()
        return [_tpl_to_dict(t) for t in templates]

    async def list_templates(self, keyword: str | None = None) -> list[dict]:
        if keyword:
            templates = await self.template_repo.search_by_keyword(keyword)
        else:
            templates = await self.template_repo.list_all()
        return [_tpl_to_dict(t) for t in templates]

    async def template_list(self, payload: TemplateListBodyRequest) -> list[dict]:
        templates = await self.template_repo.list_all()
        if payload.category_id:
            maps = await self.category_map_repo.list_by_category_id(
                payload.category_id
            )
            template_ids = {m.template_id for m in maps}
            templates = [t for t in templates if t.id in template_ids]
        if payload.dv_type:
            templates = [t for t in templates if t.dv_type == payload.dv_type]
        if payload.template_type:
            templates = [
                t for t in templates if t.template_type == payload.template_type
            ]
        if payload.keyword:
            kw = payload.keyword.lower()
            templates = [t for t in templates if kw in (t.name or "").lower()]
        return [_tpl_to_dict(t) for t in templates]

    async def update(
        self,
        payload: TemplateUpdateRequest,
    ) -> dict:
        tpl = await self.template_repo.get_by_id(payload.id)
        if tpl is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        update_data: dict[str, object] = {}
        if payload.name is not None:
            update_data["name"] = payload.name
        if payload.snapshot is not None:
            update_data["snapshot"] = payload.snapshot
        if payload.template_style is not None:
            update_data["template_style"] = payload.template_style
        if payload.template_data is not None:
            update_data["template_data"] = payload.template_data
        if payload.dynamic_data is not None:
            update_data["dynamic_data"] = payload.dynamic_data
        updated = await self.template_repo.update(tpl, update_data)
        return _tpl_to_dict(updated)

    async def name_check(self, payload: NameCheckRequest) -> str:
        templates = await self.template_repo.list_all()
        if payload.opt_type == "update" and payload.id:
            duplicates = [
                t for t in templates if t.name == payload.name and t.id != payload.id
            ]
        else:
            duplicates = [t for t in templates if t.name == payload.name]
        return "exist_all" if duplicates else "none"

    async def category_template_name_check(
        self, payload: CategoryTemplateNameCheckRequest
    ) -> str:
        return "none"

    async def delete_category(self, category_id: str) -> str:
        cat = await self.category_repo.get_by_id(category_id)
        if cat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        maps = await self.category_map_repo.list_by_category_id(category_id)
        for m in maps:
            await self.session.delete(m)
        await self.category_repo.delete(cat)
        await self.session.commit()
        return "success"

    async def batch_delete(self, payload: BatchDeleteRequest) -> None:
        template_ids = payload.template_ids or []
        categories = payload.categories or []
        for tid in template_ids:
            if categories:
                for cat_id in categories:
                    maps = await self.category_map_repo.list_by_category_id(cat_id)
                    for m in maps:
                        if m.template_id == tid:
                            await self.session.delete(m)
                remaining = await self.category_map_repo.list_by_template_id(tid)
                if not remaining:
                    tpl = await self.template_repo.get_by_id(tid)
                    if tpl:
                        await self.template_repo.delete(tpl)
            else:
                tpl = await self.template_repo.get_by_id(tid)
                if tpl:
                    await self.category_map_repo.delete_by_template_id(tid)
                    await self.template_repo.delete(tpl)
        await self.session.commit()

    async def batch_update(self, payload: BatchUpdateRequest) -> None:
        template_ids = payload.template_ids or []
        categories = payload.categories or []
        for tid in template_ids:
            existing = await self.category_map_repo.list_by_template_id(tid)
            for m in existing:
                await self.session.delete(m)
            for cat_id in categories:
                await self.category_map_repo.create({
                    "id": _new_id(),
                    "template_id": tid,
                    "category_id": cat_id,
                })
        await self.session.commit()

    async def find_categories_by_template_ids(
        self, payload: FindCategoriesByTemplateIdsRequest
    ) -> list[str]:
        stmt = (
            select(VisualizationTemplateCategoryMap.category_id)
            .where(
                VisualizationTemplateCategoryMap.template_id.in_(
                    payload.template_ids
                )
            )
            .distinct()
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all() if row[0]]

    async def check_category_template(self, category_id: str) -> bool:
        maps = await self.category_map_repo.list_by_category_id(category_id)
        return len(maps) > 0

    # ------------------------------------------------------------------
    # Store (favorites) methods
    # ------------------------------------------------------------------

    async def toggle_favorite(
        self, resource_id: int, uid: int, resource_type: int = 0
    ) -> dict:
        existing = await self.store_repo.get_by_resource(
            resource_id, uid, resource_type
        )
        if existing is not None:
            await self.store_repo.delete_by_resource(resource_id, uid, resource_type)
            return {"favorited": False}
        await self.store_repo.create({
            "id": time.time_ns(),
            "resource_id": resource_id,
            "uid": uid,
            "resource_type": resource_type,
            "time": int(time.time() * 1000),
        })
        return {"favorited": True}

    async def list_favorites(self, uid: int) -> list[dict]:
        stores = await self.store_repo.query_by_user(uid)
        return [
            {
                "id": s.id,
                "resourceId": s.resource_id,
                "uid": s.uid,
                "resourceType": s.resource_type,
                "time": s.time,
            }
            for s in stores
        ]


def _tpl_to_dict(tpl: VisualizationTemplate) -> dict:
    return {
        "id": tpl.id,
        "name": tpl.name,
        "pid": tpl.pid,
        "level": tpl.level,
        "dvType": tpl.dv_type,
        "nodeType": tpl.node_type,
        "createBy": tpl.create_by,
        "createTime": tpl.create_time,
        "snapshot": tpl.snapshot,
        "templateType": tpl.template_type,
        "templateStyle": tpl.template_style,
        "templateData": tpl.template_data,
        "dynamicData": tpl.dynamic_data,
    }


def _cat_to_dict(cat: VisualizationTemplateCategory) -> dict:
    return {
        "id": cat.id,
        "name": cat.name,
        "pid": cat.pid,
        "level": cat.level,
        "dvType": cat.dv_type,
        "nodeType": cat.node_type,
        "createBy": cat.create_by,
        "createTime": cat.create_time,
        "templateType": cat.template_type,
    }


    async def export_template(self, template_id: str) -> dict[str, object]:
        tpl = await self.template_repo.get_by_id(template_id)
        if tpl is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return {
            "name": tpl.name or "",
            "dvType": tpl.dv_type or "PANEL",
            "nodeType": tpl.node_type or "template",
            "snapshot": tpl.snapshot or "",
            "canvasStyleData": tpl.template_style or {},
            "componentData": tpl.template_data or [],
            "dynamicData": tpl.dynamic_data or {},
            "version": 3,
        }


async def get_template_service(
    session: AsyncSession = Depends(get_db),
) -> TemplateService:
    return TemplateService(session)
