from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.api_key import ApiKeyEnableEditor
from app.schemas.auth import TokenUser
from app.services.api_key_service import ApiKeyService, get_api_key_service

router = APIRouter(tags=["api-key"])


@router.post("/apiKey/generate")
async def generate_api_key(
    user: TokenUser = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> object:
    return await service.generate(user)


@router.get("/apiKey/query")
async def query_api_keys(
    user: TokenUser = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> object:
    return await service.query(user)


@router.post("/apiKey/switch")
async def switch_api_key(
    payload: ApiKeyEnableEditor,
    user: TokenUser = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> None:
    await service.switch_enable(payload, user)
    return None


@router.post("/apiKey/delete/{key_id}")
async def delete_api_key(
    key_id: int,
    user: TokenUser = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
) -> None:
    await service.delete_key(key_id, user)
    return None
