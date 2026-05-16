from __future__ import annotations

from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.log_repo import LogRepository
from app.schemas.log import LogGridRequest, LogGridVO


@final
class LogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = LogRepository(session)

    async def pager(
        self, page: int, page_size: int, request: LogGridRequest
    ) -> dict:
        rows, total = await self.repo.list_paginated(
            page,
            page_size,
            keyword=request.keyword,
            op=request.op,
            uid=request.uid,
            oid=request.oid,
        )
        items = [
            LogGridVO.model_validate(r).model_dump(by_alias=True) for r in rows
        ]
        return {
            "pager": {
                "totalItem": total,
                "pageSize": page_size,
                "totalPage": (total + page_size - 1) // page_size,
                "currentPage": page,
            },
            "data": items,
        }

    async def export_logs(self, request: LogGridRequest) -> None:
        """Stub - log export not implemented in basic version."""
        pass

    async def log_options(self) -> list[dict]:
        """Return operation type tree."""
        return [
            {"value": "LOGIN", "label": "登录", "children": []},
            {"value": "VIEW", "label": "查看", "children": []},
            {
                "value": "CREATE",
                "label": "创建",
                "children": [
                    {"value": "CREATE-DASHBOARD", "label": "创建仪表板", "children": []},
                    {"value": "CREATE-DATASET", "label": "创建数据集", "children": []},
                    {"value": "CREATE-DATASOURCE", "label": "创建数据源", "children": []},
                ],
            },
            {
                "value": "MODIFY",
                "label": "修改",
                "children": [
                    {"value": "MODIFY-DASHBOARD", "label": "修改仪表板", "children": []},
                    {"value": "MODIFY-DATASET", "label": "修改数据集", "children": []},
                ],
            },
            {"value": "DELETE", "label": "删除", "children": []},
            {"value": "SHARE", "label": "分享", "children": []},
            {"value": "EXPORT", "label": "导出", "children": []},
        ]


async def get_log_service(session: AsyncSession = Depends(get_db)) -> LogService:
    return LogService(session)
