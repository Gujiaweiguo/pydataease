from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.template import (
    BatchDeleteRequest,
    BatchUpdateRequest,
    CategoryFormRequest,
    CategoryTemplateNameCheckRequest,
    FindCategoriesByTemplateIdsRequest,
    FindCategoriesRequest,
    NameCheckRequest,
    StoreToggleRequest,
    TemplateFindRequest,
    TemplateListBodyRequest,
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


@router.post("/templateManage/findCategories")
async def template_find_categories(
    payload: FindCategoriesRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.find_categories(payload)


@router.post("/templateManage/categoryForm")
async def template_category_form(
    payload: CategoryFormRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.category_form(payload.category_id)


@router.post("/templateManage/delete/{template_id}/{category_id}")
async def template_delete(
    template_id: str,
    category_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> None:
    await service.delete(template_id, category_id)


@router.get("/templateManage/findOne/{template_id}")
async def template_find_one(
    template_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    result = await service.find_one(template_id)
    return result


@router.post("/templateManage/find")
async def template_find(
    payload: TemplateFindRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.find_by_body(payload)


@router.post("/templateManage/list")
async def template_list(
    payload: TemplateListRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.list_templates(payload.keyword)


@router.post("/templateManage/templateList")
async def template_list_body(
    payload: TemplateListBodyRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.template_list(payload)


@router.post("/templateManage/update")
async def template_update(
    payload: TemplateUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.update(payload)


@router.post("/templateManage/nameCheck")
async def template_name_check(
    payload: NameCheckRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.name_check(payload)


@router.post("/templateManage/categoryTemplateNameCheck")
async def category_template_name_check(
    payload: CategoryTemplateNameCheckRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.category_template_name_check(payload)


@router.post("/templateManage/deleteCategory/{category_id}")
async def delete_category(
    category_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.delete_category(category_id)


@router.post("/templateManage/batchDelete")
async def batch_delete(
    payload: BatchDeleteRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.batch_delete(payload)


@router.post("/templateManage/batchUpdate")
async def batch_update(
    payload: BatchUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.batch_update(payload)


@router.post("/templateManage/findCategoriesByTemplateIds")
async def find_categories_by_template_ids(
    payload: FindCategoriesByTemplateIdsRequest,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.find_categories_by_template_ids(payload)


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


@router.get("/templateManage/export/{template_id}")
async def export_template(
    template_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TemplateService = Depends(get_template_service),
) -> object:
    return await service.export_template(template_id)


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
