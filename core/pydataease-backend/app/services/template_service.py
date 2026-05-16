from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.template import (
    VisualizationTemplate,
    VisualizationTemplateCategory,
)
from app.repositories.store_repo import StoreRepository
from app.repositories.template_repo import (
    TemplateCategoryMapRepository,
    TemplateCategoryRepository,
    TemplateRepository,
)
from app.schemas.auth import TokenUser
from app.schemas.template import (
    TemplateSaveRequest,
    TemplateTreeNode,
    TemplateUpdateRequest,
)


def _new_id() -> str:
    return str(time.time_ns())


def _build_tree(
    nodes: list[VisualizationTemplate | VisualizationTemplateCategory],
) -> list[TemplateTreeNode]:
    """Build a tree from flat list based on pid relationships."""
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
        """Build tree of templates with categories."""
        categories = await self.category_repo.list_all()

        # Build category tree
        cat_tree = _build_tree(categories)  # type: ignore[arg-type]

        # Attach templates to their categories via category_map
        for cat in cat_tree:
            await self._attach_templates_to_node(cat)

        return [n.model_dump(by_alias=True) for n in cat_tree]

    async def _attach_templates_to_node(self, node: TemplateTreeNode) -> None:
        """Recursively attach templates to category tree nodes."""
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
        """Create new template."""
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
        """Return list of {id, name} for all templates."""
        templates = await self.template_repo.list_all()
        return [{"id": t.id, "name": t.name} for t in templates]

    async def categories(self) -> list[dict]:
        """Return list of categories as tree."""
        categories = await self.category_repo.list_all()
        tree = _build_tree(categories)  # type: ignore[arg-type]
        return [n.model_dump(by_alias=True) for n in tree]

    async def category_form(self, category_id: str) -> dict:
        """Return category detail + its templates."""
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

    async def delete(self, template_id: str) -> None:
        """Delete template and its category maps."""
        tpl = await self.template_repo.get_by_id(template_id)
        if tpl is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        await self.category_map_repo.delete_by_template_id(template_id)
        await self.template_repo.delete(tpl)

    async def find_one(self, template_id: str) -> dict | None:
        """Return single template detail."""
        tpl = await self.template_repo.get_by_id(template_id)
        if tpl is None:
            return None
        return _tpl_to_dict(tpl)

    async def find(self, template_id: str) -> dict | None:
        """Return template with full data (alias for find_one)."""
        return await self.find_one(template_id)

    async def list_templates(self, keyword: str | None = None) -> list[dict]:
        """Search templates by keyword."""
        if keyword:
            templates = await self.template_repo.search_by_keyword(keyword)
        else:
            templates = await self.template_repo.list_all()
        return [_tpl_to_dict(t) for t in templates]

    async def update(
        self,
        payload: TemplateUpdateRequest,
    ) -> dict:
        """Update template."""
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

    async def check_category_template(self, category_id: str) -> bool:
        """Check if category has templates."""
        maps = await self.category_map_repo.list_by_category_id(category_id)
        return len(maps) > 0

    # ------------------------------------------------------------------
    # Store (favorites) methods
    # ------------------------------------------------------------------

    async def toggle_favorite(
        self, resource_id: int, uid: int, resource_type: int = 0
    ) -> dict:
        """Add or remove favorite."""
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
        """Return list of favorited resources."""
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


async def get_template_service(
    session: AsyncSession = Depends(get_db),
) -> TemplateService:
    return TemplateService(session)
