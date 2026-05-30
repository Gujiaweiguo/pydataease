from __future__ import annotations

import hmac
import logging
import secrets
import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.share import XpackShare
from app.repositories.share_repo import ShareRepository, ShareTicketRepository
from app.repositories.embed_config_repo import EmbedConfigRepository
from app.schemas.share import (
    ProxyInfoResponse,
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
    TicketValidVO,
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

    async def proxy_info(
        self, payload: ShareProxyInfoRequest
    ) -> tuple[ProxyInfoResponse, str] | None:
        share = await self.share_repo.get_by_uuid(payload.uuid)
        if share is None:
            return None

        current_ms = int(time.time() * 1000)

        # Expiration check
        is_expired = share.exp is not None and share.exp < current_ms

        # Password validation
        pwd_valid = False
        if not share.pwd:
            pwd_valid = True
        elif payload.ciphertext:
            try:
                from app.utils.rsa_utils import decrypt_rsa
                decrypted = decrypt_rsa(payload.ciphertext)
                # Frontend encrypts "uuid,password" — extract password part
                if "," in decrypted:
                    _, password = decrypted.split(",", 1)
                else:
                    password = decrypted
                pwd_valid = hmac.compare_digest(password, share.pwd)
            except Exception:
                logger.warning("Failed to decrypt share password ciphertext")
                pwd_valid = False

        # Ticket validation
        ticket_vo = TicketValidVO()
        if payload.ticket:
            ticket_record = await self.ticket_repo.get_by_ticket(payload.ticket)
            if ticket_record is None or ticket_record.uuid != share.uuid:
                ticket_vo = TicketValidVO(ticket_valid=False, ticket_exp=False)
            else:
                ticket_expired = (
                    ticket_record.exp is not None and ticket_record.exp < current_ms
                )
                ticket_args = None
                if ticket_record.args is not None:
                    import json

                    ticket_args = json.dumps(ticket_record.args) if not isinstance(ticket_record.args, str) else ticket_record.args
                ticket_vo = TicketValidVO(
                    ticket_valid=not ticket_expired,
                    ticket_exp=ticket_expired,
                    args=ticket_args,
                )

        # Resource type
        resource_type = "dashboard" if share.type == 0 else "dataV"

        # Embed control enforcement
        share_disable = False
        embed_type = self._map_share_type_to_embed_type(share.type)
        if embed_type:
            embed_repo = EmbedConfigRepository(self.session)
            embed_config = await embed_repo.get_by_resource_type(embed_type)
            if embed_config is not None:
                if not embed_config.embed_enabled:
                    share_disable = True
                elif payload.domain and embed_config.allowed_domains:
                    if payload.domain not in embed_config.allowed_domains:
                        share_disable = True

        # Iframe error flag
        in_iframe_error = bool(payload.in_iframe)

        # Generate link token JWT — only after successful auth
        if is_expired or (share.pwd and not pwd_valid) or (share.ticket_require and not ticket_vo.ticket_valid):
            link_token = ""
        else:
            link_token = self._generate_link_token(share, current_ms)

        response = ProxyInfoResponse(
            resource_id=str(share.resource_id),
            uid=str(share.creator),
            exp=is_expired,
            pwd_valid=pwd_valid,
            type=resource_type,
            in_iframe_error=in_iframe_error,
            share_disable=share_disable,
            pe_require_valid=True,
            ticket_valid_vo=ticket_vo,
            uuid=share.uuid,
        )
        return response, link_token

    def _generate_link_token(self, share: "XpackShare", _current_ms: int) -> str:
        from jose import jwt as jose_jwt

        from app.settings.config import get_settings

        settings = get_settings()

        token_exp_s = int(time.time()) + 86400  # 24 hours
        if share.exp is not None:
            share_exp_s = share.exp // 1000
            token_exp_s = min(token_exp_s, share_exp_s)

        claims = {
            "uid": share.creator,
            "oid": share.oid,
            "resourceId": share.resource_id,
            "exp": token_exp_s,
        }
        return jose_jwt.encode(claims, settings.share_secret_key, algorithm=settings.jwt_algorithm)

    async def save(self, payload: ShareCreateRequest, user: TokenUser) -> ShareResponse:
        clamped_exp = await self._clamp_expiry(payload.type, payload.exp)
        existing = await self.share_repo.get_by_resource_id(payload.resource_id)
        if existing is not None:
            update_data: dict[str, object] = {
                "creator": user.user_id,
                "time": _new_share_id(),
            }
            if payload.exp is not None:
                update_data["exp"] = clamped_exp
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
        # BUG-011 fix: Enforce UUID uniqueness on create
        if payload.uuid:
            existing_uuid = await self.share_repo.get_by_uuid(share_uuid)
            if existing_uuid is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Share UUID already exists",
                )
        created = await self.share_repo.create({
            "id": _new_share_id(),
            "creator": user.user_id,
            "time": _new_share_id(),
            "exp": clamped_exp,
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
        resp = ShareResponse.model_validate(share)
        resp.pwd = None  # BUG-013 fix: Don't leak password in public endpoints
        return resp

    async def get_by_id(self, resource_id: int) -> ShareResponse | None:
        share = await self.share_repo.get_by_resource_id(resource_id)
        if share is None:
            return None
        return ShareResponse.model_validate(share)

    async def proxy(self, uuid: str) -> ShareResponse | None:
        share = await self.share_repo.get_by_uuid(uuid)
        if share is None:
            return None
        resp = ShareResponse.model_validate(share)
        resp.pwd = None  # BUG-013 fix: Don't leak password in public endpoints
        return resp

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
        # BUG-010 fix: Reject resolve() when ticket is required — use proxy_info flow
        if share.ticket_require:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ticket required — use proxy_info flow",
            )
        await self.record_access(uuid)
        return ShareResponse.model_validate(share)

    async def validate_password(self, payload: dict) -> dict:
        # Decrypt RSA ciphertext → "uuid,password"
        ciphertext = payload.get("ciphertext", "")
        if not ciphertext:
            return {"code": 1, "data": None, "msg": "Missing ciphertext"}
        try:
            from app.utils.rsa_utils import decrypt_rsa

            decrypted = decrypt_rsa(ciphertext)
            if "," not in decrypted:
                return {"code": 1, "data": None, "msg": "Invalid ciphertext format"}
            uuid, password = decrypted.split(",", 1)
        except Exception:
            logger.warning("Failed to decrypt share password ciphertext")
            return {"code": 1, "data": None, "msg": "Decryption failed"}

        share = await self.share_repo.get_by_uuid(uuid)
        if share is None:
            return {"code": 1, "data": None, "msg": "Share not found"}
        current_ms = int(time.time() * 1000)
        if share.exp is not None and share.exp < current_ms:
            return {"code": 1, "data": None, "msg": "Share has expired"}
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
            # Update access time on all tickets for this share
            tickets = await self.ticket_repo.list_by_uuid(uuid)
            for ticket in tickets:
                await self.ticket_repo.update_access_time(ticket.id)
            # Increment access count on the share itself
            await self.share_repo.increment_access_count(uuid)
        except Exception:
            logging.exception("Failed to record share access for uuid=%s", uuid)
            # BUG-036 fix: Rollback to isolate this transaction
            await self.session.rollback()

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

        embed_type = self._map_share_type_to_embed_type(share.type)
        if embed_type:
            embed_repo = EmbedConfigRepository(self.session)
            embed_config = await embed_repo.get_by_resource_type(embed_type)
            if embed_config is not None and not embed_config.embed_enabled:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Embedding is disabled for this resource type",
                )

        from app.settings.config import get_settings
        settings = get_settings()

        token_exp_s = int(time.time()) + 86400  # 24 hours
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

    # ------------------------------------------------------------------
    # New share management methods
    # ------------------------------------------------------------------

    async def switcher(self, resource_id: int, user: TokenUser) -> dict:
        """Toggle share on/off for a resource."""
        share = await self.share_repo.get_by_resource_id(resource_id)
        if share:
            await self.delete(ShareDeleteRequest(resource_id=resource_id))
            return {"status": "deleted"}
        uuid = _new_share_uuid()
        pwd = secrets.token_urlsafe(4)[:4]
        payload = ShareCreateRequest(
            resource_id=resource_id, uuid=uuid, auto_pwd=True, pwd=pwd
        )
        result = await self.save(payload, user)
        return {"status": "created", "data": result}

    async def edit_exp(self, resource_id: int, exp: int) -> ShareResponse | None:
        share = await self.share_repo.get_by_resource_id(resource_id)
        if share is None:
            return None
        clamped = await self._clamp_expiry(share.type, exp if exp > 0 else None)
        updated = await self.share_repo.update(share, {"exp": clamped})
        return ShareResponse.model_validate(updated)

    async def edit_pwd(
        self, resource_id: int, pwd: str, auto_pwd: bool
    ) -> ShareResponse | None:
        share = await self.share_repo.get_by_resource_id(resource_id)
        if share is None:
            return None
        updated = await self.share_repo.update(
            share, {"pwd": pwd if pwd else None, "auto_pwd": auto_pwd}
        )
        return ShareResponse.model_validate(updated)

    async def edit_uuid(self, resource_id: int, uuid: str) -> str:
        """Validate and update share UUID. Returns empty string on success, error message on failure."""
        if not uuid.isalnum() or len(uuid) < 8 or len(uuid) > 16:
            return "链接只能包含8-16位字母和数字"
        existing = await self.share_repo.get_by_uuid(uuid)
        if existing is not None and existing.resource_id != resource_id:
            return "链接已存在"
        share = await self.share_repo.get_by_resource_id(resource_id)
        if share is None:
            return "分享不存在"
        await self.share_repo.update(share, {"uuid": uuid})
        return ""

    async def query_shares(self) -> list[ShareResponse]:
        rows = await self.share_repo.list_all_ordered()
        return [ShareResponse.model_validate(s) for s in rows]

    async def query_relation_by_user(self, uid: int) -> dict[str, str]:
        rows = await self.share_repo.list_by_creator(uid)
        return {str(s.resource_id): s.uuid for s in rows}

    async def enable_ticket(self, resource_id: str, require: bool) -> None:
        try:
            rid = int(resource_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid resource_id") from None
        share = await self.share_repo.get_by_resource_id(rid)
        if share is not None:
            await self.share_repo.update(share, {"ticket_require": require})

    @staticmethod
    def generate_temp_ticket() -> str:
        import string

        return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

    @staticmethod
    def _map_share_type_to_embed_type(share_type: int) -> str | None:
        mapping = {0: "dashboard", 1: "datav"}
        return mapping.get(share_type)

    async def _clamp_expiry(self, share_type: int | None, exp: int | None) -> int | None:
        if exp is None or exp <= 0:
            return exp
        embed_type = self._map_share_type_to_embed_type(share_type) if share_type is not None else None
        if not embed_type:
            return exp
        embed_repo = EmbedConfigRepository(self.session)
        embed_config = await embed_repo.get_by_resource_type(embed_type)
        if embed_config is None or embed_config.max_expiry_hours is None:
            return exp
        max_ms = embed_config.max_expiry_hours * 3600 * 1000
        return min(exp, max_ms)


async def get_share_service(session: AsyncSession = Depends(get_db)) -> ShareService:
    return ShareService(session)
