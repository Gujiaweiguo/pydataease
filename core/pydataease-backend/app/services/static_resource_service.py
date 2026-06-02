from __future__ import annotations

from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.static_resource_repo import StaticResourceRepository
from app.schemas.static_resource import StaticResourceUploadRequest


@final
class StaticResourceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.resource_repo = StaticResourceRepository(session)

    async def upload(self, file_id: str, payload: StaticResourceUploadRequest) -> dict:
        """Save base64 content to static_resource."""
        existing = await self.resource_repo.get_by_id(file_id)
        if existing is not None:
            updated = await self.resource_repo.update(
                existing, {"content": payload.content}
            )
            return _resource_to_dict(updated)

        data: dict[str, object] = {
            "id": file_id,
            "content": payload.content,
        }
        resource = await self.resource_repo.create(data)
        return _resource_to_dict(resource)

    async def find_as_base64(self, resource_id: str) -> dict[str, str]:
        """Return base64 content for a resource."""
        resource = await self.resource_repo.get_by_id(resource_id)
        if resource is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Static resource not found",
            )
        return {"resourceId": resource.id, "content": resource.content or ""}

    async def get_resource_by_id(self, resource_id: str):
        """Return the raw StaticResource row, or None if not found."""
        return await self.resource_repo.get_by_id(resource_id)


def _resource_to_dict(resource) -> dict:
    return {
        "id": resource.id,
        "name": resource.name,
        "content": resource.content,
    }


async def get_static_resource_service(
    session: AsyncSession = Depends(get_db),
) -> StaticResourceService:
    return StaticResourceService(session)
