from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.share import (
    ShareCreateRequest,
    ShareDeleteRequest,
    ShareDetailRequest,
    ShareProxyInfoRequest,
    ShareTicketDeleteRequest,
    ShareTicketDetailRequest,
    ShareTicketSaveRequest,
    ShareViewDetailRequest,
)
from app.services.share_service import ShareService, get_share_service

router = APIRouter(prefix="/share", tags=["share"])


class EmbedTokenRequest(BaseModel):
    uuid: str


@router.get("/status/{resource_id}")
async def share_status(
    resource_id: int,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.get_status(resource_id)


@router.post("/validate")
async def validate_share_password(
    payload: dict,
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.validate_password(payload)


@router.post("/proxyInfo")
async def proxy_info(
    payload: ShareProxyInfoRequest,
    service: ShareService = Depends(get_share_service),
) -> object:
    result = await service.proxy_info(payload)
    if result is None:
        return None
    proxy_info_response, link_token = result
    response = JSONResponse(
        content=proxy_info_response.model_dump(by_alias=True)
    )
    response.headers["x-de-link-token"] = link_token
    return response


@router.post("/save")
async def save_share(
    payload: ShareCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.save(payload, user)


@router.post("/detail")
async def detail_share(
    payload: ShareDetailRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.detail(payload)


@router.post("/delete")
async def delete_share(
    payload: ShareDeleteRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> None:
    await service.delete(payload)


@router.post("/viewDetail")
async def view_detail(
    payload: ShareViewDetailRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.view_detail(payload)


@router.get("/detail/{resource_id}")
async def get_share_detail(
    resource_id: int,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.get_by_id(resource_id)


@router.post("/saveTicket")
async def save_ticket(
    payload: ShareTicketSaveRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.save_ticket(payload)


@router.post("/deleteTicket")
async def delete_ticket(
    payload: ShareTicketDeleteRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> None:
    await service.delete_ticket(payload)


@router.post("/detailTicket")
async def detail_tickets(
    payload: ShareTicketDetailRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.detail_tickets(payload)


@router.get("/proxy/{uuid}")
async def proxy_share(
    uuid: str,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    return await service.proxy(uuid)


@router.get("/view/{uuid}")
async def view_share(
    uuid: str,
    request: Request,
    password: str | None = Query(default=None),
    ticket: str | None = Query(default=None),
    service: ShareService = Depends(get_share_service),
) -> object:
    share = await service.resolve(uuid, password=password)
    resource_info = await service.get_resource_data(share)
    return {"share": share, "resource": resource_info}


@router.post("/embedToken")
async def generate_embed_token(
    payload: EmbedTokenRequest,
    user: TokenUser = Depends(get_current_user),
    service: ShareService = Depends(get_share_service),
) -> object:
    token = await service.generate_embed_token(payload.uuid)
    return {"token": token}
