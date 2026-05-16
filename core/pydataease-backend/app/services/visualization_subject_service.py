from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.visualization_subject import VisualizationSubject
from app.repositories.visualization_subject_repo import VisualizationSubjectRepository
from app.schemas.auth import TokenUser
from app.schemas.visualization_subject import SubjectUpdateRequest


def _subject_to_dict(s: VisualizationSubject) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "type": s.type,
        "details": s.details,
        "deleteFlag": s.delete_flag,
        "coverUrl": s.cover_url,
        "createNum": s.create_num,
        "createTime": s.create_time,
        "createBy": s.create_by,
        "updateTime": s.update_time,
        "updateBy": s.update_by,
    }


@final
class VisualizationSubjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = VisualizationSubjectRepository(session)

    async def query(self) -> list[dict]:
        """List all non-deleted subjects."""
        rows = await self.repo.list_active()
        return [_subject_to_dict(s) for s in rows]

    async def query_subject_with_group(self) -> list[list[dict]]:
        """Return subjects grouped into arrays of 4."""
        rows = await self.repo.list_active()
        result: list[list[dict]] = []
        group: list[dict] = []
        for row in rows:
            group.append(_subject_to_dict(row))
            if len(group) == 4:
                result.append(group)
                group = []
        if group:
            result.append(group)
        return result

    async def update_subject(
        self, payload: SubjectUpdateRequest, user: TokenUser
    ) -> dict:
        """Create (if no id) or update (if id provided) subject."""
        if payload.id:
            # Update existing
            entity = await self.repo.get_by_id(payload.id)
            if entity is None:
                raise HTTPException(404, "Subject not found")
            update_data: dict = {}
            if payload.name is not None:
                update_data["name"] = payload.name
            if payload.details is not None:
                update_data["details"] = payload.details
            if payload.cover_url is not None:
                update_data["cover_url"] = payload.cover_url
            update_data["update_time"] = int(time.time() * 1000)
            update_data["update_by"] = str(user.user_id)
            updated = await self.repo.update(entity, update_data)
            return _subject_to_dict(updated)
        else:
            # Create new - check name uniqueness
            if payload.name:
                existing = await self.repo.get_by_name(payload.name)
                if existing:
                    raise HTTPException(400, "Subject name already exists")
            data = {
                "id": str(time.time_ns()),
                "name": payload.name,
                "type": payload.type or "self",
                "details": payload.details,
                "cover_url": payload.cover_url,
                "create_num": 0,
                "create_time": int(time.time() * 1000),
                "create_by": str(user.user_id),
                "delete_flag": False,
            }
            created = await self.repo.create(data)
            return _subject_to_dict(created)

    async def delete_subject(self, subject_id: str) -> None:
        entity = await self.repo.get_by_id(subject_id)
        if entity is None:
            raise HTTPException(404, "Subject not found")
        await self.repo.delete(entity)


async def get_subject_service(
    session: AsyncSession = Depends(get_db),
) -> VisualizationSubjectService:
    return VisualizationSubjectService(session)
