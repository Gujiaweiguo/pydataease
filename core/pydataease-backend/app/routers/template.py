from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.template import (
    CategoryFormRequest,
    StoreToggleRequest,
    TemplateListRequest,
    TemplateSaveRequest,
    TemplateUpdateRequest,
)
from app.services.template_service import TemplateService, get_template_service

router = APIRouter(tags=["template"])


# ------------------------------------------------------------------
# Template management endpoints
# ------------------------------------------------------------------


@router.post("/templateManage/tree")
async def template_tree(
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.tree()


@router.post("/templateManage/save")
async def template_save(
    payload: TemplateSaveRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.save(payload, user)


@router.post("/templateManage/nameList")
async def template_name_list(
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.name_list()


@router.post("/templateManage/categories")
async def template_categories(
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.categories()


@router.post("/templateManage/categoryForm")
async def template_category_form(
    payload: CategoryFormRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.category_form(payload.category_id)


@router.post("/templateManage/delete/{template_id}")
async def template_delete(
    template_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> None:
    await service.delete(template_id)


@router.post("/templateManage/findOne/{template_id}")
async def template_find_one(
    template_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    result = await service.find_one(template_id)
    return result


@router.post("/templateManage/find/{template_id}")
async def template_find(
    template_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    result = await service.find(template_id)
    return result


@router.post("/templateManage/list")
async def template_list(
    payload: TemplateListRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.list_templates(payload.keyword)


@router.post("/templateManage/update")
async def template_update(
    payload: TemplateUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.update(payload)


@router.post("/templateManage/checkCategoryTemplate/{category_id}")
async def check_category_template(
    category_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    has_templates = await service.check_category_template(category_id)
    return has_templates


# ------------------------------------------------------------------
# Store (favorites) endpoints
# ------------------------------------------------------------------


@router.post("/store/toggleFavorite")
async def store_toggle_favorite(
    payload: StoreToggleRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.toggle_favorite(
        payload.resource_id, user.user_id, payload.resource_type
    )


@router.post("/store/list")
async def store_list(
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.list_favorites(user.user_id)
