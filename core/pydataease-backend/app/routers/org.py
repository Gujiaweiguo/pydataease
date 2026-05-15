from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.repositories.org_repo import OrgRepository
from app.schemas.auth import TokenUser
from app.schemas.org import OrgCreateRequest, OrgEditRequest, OrgMountedRequest, OrgTreeRequest
from app.settings.config import get_settings
from app.services.org_service import OrgService, get_org_service

router = APIRouter(prefix="/org", tags=["org"])


def require_org_management_enabled() -> None:
    if not get_settings().org_management_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Org management is disabled")


@router.post("/page/tree")
async def org_tree(
    _payload: OrgTreeRequest | None = None,
    _org_management_enabled: None = Depends(require_org_management_enabled),
    user: TokenUser = Depends(get_current_user),
    service: OrgService = Depends(get_org_service),
) -> object:
    return await service.tree(user)


@router.post("/page/create")
async def create_org(
    payload: OrgCreateRequest,
    _org_management_enabled: None = Depends(require_org_management_enabled),
    _user: TokenUser = Depends(get_current_user),
    service: OrgService = Depends(get_org_service),
) -> object:
    return await service.create(payload)


@router.post("/page/edit")
async def edit_org(
    payload: OrgEditRequest,
    _org_management_enabled: None = Depends(require_org_management_enabled),
    _user: TokenUser = Depends(get_current_user),
    service: OrgService = Depends(get_org_service),
) -> object:
    return await service.edit(payload)


@router.post("/page/delete/{oid}")
async def delete_org(
    oid: int,
    _org_management_enabled: None = Depends(require_org_management_enabled),
    _user: TokenUser = Depends(get_current_user),
    service: OrgService = Depends(get_org_service),
) -> None:
    await service.delete(oid)


@router.get("/resourceExist/{oid}")
async def resource_exist(
    oid: int,
    _org_management_enabled: None = Depends(require_org_management_enabled),
    _user: TokenUser = Depends(get_current_user),
    service: OrgService = Depends(get_org_service),
) -> bool:
    return await service.resource_exist(oid)


@router.post("/mounted")
async def mounted_orgs(
    payload: OrgMountedRequest | None = None,
    _org_management_enabled: None = Depends(require_org_management_enabled),
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    repository = OrgRepository(session)
    orgs = await (repository.list_all() if user.user_id == 1 else repository.get_user_orgs(user.user_id))
    keyword = (payload.keyword.strip() if payload and payload.keyword else "")
    if keyword:
        orgs = [org for org in orgs if keyword in org.name]
    return [{"id": org.id, "name": org.name, "pid": org.pid or 0} for org in orgs]
