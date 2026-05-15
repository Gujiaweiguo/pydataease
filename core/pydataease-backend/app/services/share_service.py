from __future__ import annotations

import hmac
import logging
import secrets
import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.share_repo import ShareRepository, ShareTicketRepository
from app.schemas.share import (
    ShareCreateRequest,
    ShareDeleteRequest,
    ShareDetailRequest,
    ShareProxyInfoRequest,
    ShareResponse,
    ShareTicketDeleteRequest,
    ShareTicketDetailRequest,
    ShareTicketResponse,
    ShareTicketSaveRequest,
    ShareViewDetailRequest,
)
from app.schemas.auth import TokenUser

logger = logging.getLogger(__name__)


def _new_share_id() -> int:
    return time.time_ns()


def _new_share_uuid() -> str:
    return secrets.token_urlsafe(8)[:16]


@final
class ShareService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.share_repo = ShareRepository(session)
        self.ticket_repo = ShareTicketRepository(session)

    async def proxy_info(self, payload: ShareProxyInfoRequest) -> ShareResponse | None:
        share = await self.share_repo.get_by_uuid(payload.uuid)
        if share is None:
            return None
        return ShareResponse.model_validate(share)

    async def save(self, payload: ShareCreateRequest, user: TokenUser) -> ShareResponse:
        existing = await self.share_repo.get_by_resource_id(payload.resource_id)
        if existing is not None:
            update_data: dict[str, object] = {
                "creator": user.user_id,
                "time": _new_share_id(),
            }
            if payload.exp is not None:
                update_data["exp"] = payload.exp
            if payload.pwd is not None:
                update_data["pwd"] = payload.pwd
            if payload.auto_pwd is not None:
                update_data["auto_pwd"] = payload.auto_pwd
            if payload.type is not None:
                update_data["type"] = payload.type
            if payload.oid is not None:
                update_data["oid"] = payload.oid
            updated = await self.share_repo.update(existing, update_data)
            return ShareResponse.model_validate(updated)

        share_uuid = payload.uuid or _new_share_uuid()
        created = await self.share_repo.create({
            "id": _new_share_id(),
            "creator": user.user_id,
            "time": _new_share_id(),
            "exp": payload.exp,
            "uuid": share_uuid,
            "pwd": payload.pwd,
            "resource_id": payload.resource_id,
            "oid": payload.oid,
            "type": payload.type,
            "auto_pwd": payload.auto_pwd,
        })
        return ShareResponse.model_validate(created)

    async def detail(self, payload: ShareDetailRequest) -> ShareResponse | None:
        share = await self.share_repo.get_by_resource_id(payload.resource_id)
        if share is None:
            return None
        return ShareResponse.model_validate(share)

    async def delete(self, payload: ShareDeleteRequest) -> None:
        share = await self.share_repo.get_by_resource_id(payload.resource_id)
        if share is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Share not found"
            )
        tickets = await self.ticket_repo.list_by_uuid(share.uuid)
        for ticket in tickets:
            await self.ticket_repo.delete(ticket)
        await self.share_repo.delete(share)

    async def view_detail(self, payload: ShareViewDetailRequest) -> ShareResponse | None:
        share = await self.share_repo.get_by_uuid(payload.uuid)
        if share is None:
            return None
        return ShareResponse.model_validate(share)

    async def get_by_id(self, resource_id: int) -> ShareResponse | None:
        share = await self.share_repo.get_by_resource_id(resource_id)
        if share is None:
            return None
        return ShareResponse.model_validate(share)

    async def proxy(self, uuid: str) -> ShareResponse | None:
        share = await self.share_repo.get_by_uuid(uuid)
        if share is None:
            return None
        return ShareResponse.model_validate(share)

    async def resolve(
        self, uuid: str, password: str | None = None
    ) -> ShareResponse:
        share = await self.share_repo.get_by_uuid(uuid)
        if share is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Share not found"
            )
        current_ms = int(time.time() * 1000)
        if share.exp is not None and share.exp < current_ms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Share has expired"
            )
        if share.pwd:
            if not password or not hmac.compare_digest(share.pwd, password):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Password incorrect",
                )
        await self.record_access(uuid)
        return ShareResponse.model_validate(share)

    async def validate_password(self, payload: dict) -> dict:
        uuid = payload.get("uuid", "")
        share = await self.share_repo.get_by_uuid(uuid)
        if share is None:
            return {"code": 1, "data": None, "msg": "Share not found"}
        current_ms = int(time.time() * 1000)
        if share.exp is not None and share.exp < current_ms:
            return {"code": 1, "data": None, "msg": "Share has expired"}
        password = payload.get("password", "") or ""
        if not share.pwd:
            return {"code": 0, "data": True, "msg": ""}
        if hmac.compare_digest(share.pwd, password):
            return {"code": 0, "data": True, "msg": ""}
        return {"code": 1, "data": False, "msg": "Password incorrect"}

    async def get_status(self, resource_id: int) -> dict | None:
        share = await self.share_repo.get_by_resource_id(resource_id)
        if share is None:
            return None
        return {
            "uuid": share.uuid,
            "exp": share.exp,
            "has_pwd": share.pwd is not None,
            "auto_pwd": share.auto_pwd,
        }

    async def record_access(
        self, uuid: str, client_ip: str | None = None
    ) -> None:
        try:
            logger.info("Share access: uuid=%s ip=%s", uuid, client_ip)
            tickets = await self.ticket_repo.list_by_uuid(uuid)
            for ticket in tickets:
                await self.ticket_repo.update_access_time(ticket.id)
        except Exception:
            logging.exception("Failed to record share access for uuid=%s", uuid)

    async def save_ticket(self, payload: ShareTicketSaveRequest) -> ShareTicketResponse:
        if payload.generate_new or payload.uuid is None:
            created = await self.ticket_repo.create({
                "id": _new_share_id(),
                "uuid": payload.uuid or "",
                "ticket": payload.ticket,
                "exp": payload.exp,
                "args": payload.args,
            })
            return ShareTicketResponse.model_validate(created)

        existing = await self.ticket_repo.get_by_ticket(payload.ticket)
        if existing is not None:
            update_data: dict[str, object] = {}
            if payload.exp is not None:
                update_data["exp"] = payload.exp
            if payload.args is not None:
                update_data["args"] = payload.args
            if update_data:
                updated = await self.ticket_repo.update(existing, update_data)
                return ShareTicketResponse.model_validate(updated)
            return ShareTicketResponse.model_validate(existing)

        created = await self.ticket_repo.create({
            "id": _new_share_id(),
            "uuid": payload.uuid,
            "ticket": payload.ticket,
            "exp": payload.exp,
            "args": payload.args,
        })
        return ShareTicketResponse.model_validate(created)

    async def delete_ticket(self, payload: ShareTicketDeleteRequest) -> None:
        ticket = await self.ticket_repo.get_by_ticket(payload.ticket)
        if ticket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
            )
        await self.ticket_repo.delete(ticket)

    async def get_resource_data(self, share: ShareResponse) -> dict:
        resource_type = "dashboard" if share.type == 0 else "chart"
        return {"resource_id": share.resource_id, "resource_type": resource_type}

    async def generate_embed_token(self, uuid: str) -> str:
        from jose import jwt as jose_jwt

        share = await self.share_repo.get_by_uuid(uuid)
        if share is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Share not found"
            )
        current_ms = int(time.time() * 1000)
        if share.exp is not None and share.exp < current_ms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Share has expired"
            )

        from app.settings.config import get_settings
        settings = get_settings()

        token_exp_s = int(time.time()) + 3600
        if share.exp is not None:
            share_exp_s = share.exp // 1000
            token_exp_s = min(token_exp_s, share_exp_s)

        claims = {
            "resourceId": share.resource_id,
            "uuid": share.uuid,
            "uid": share.creator,
            "oid": share.oid,
            "exp": token_exp_s,
        }
        return jose_jwt.encode(claims, settings.share_secret_key, algorithm=settings.jwt_algorithm)

    async def detail_tickets(
        self, payload: ShareTicketDetailRequest
    ) -> list[ShareTicketResponse]:
        tickets = await self.ticket_repo.list_by_uuid(payload.uuid)
        return [ShareTicketResponse.model_validate(t) for t in tickets]


async def get_share_service(session: AsyncSession = Depends(get_db)) -> ShareService:
    return ShareService(session)
