from __future__ import annotations

import os

import pytest
from jose import jwt  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _now_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.repositories.share_repo import ShareRepository, ShareTicketRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.share import (  # pyright: ignore[reportImplicitRelativeImport]
    ShareCreateRequest,
    ShareDeleteRequest,
    ShareDetailRequest,
    ShareProxyInfoRequest,
    ShareTicketDeleteRequest,
    ShareTicketDetailRequest,
    ShareTicketSaveRequest,
    ShareViewDetailRequest,
)
from app.services.share_service import ShareService  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.config import get_settings  # pyright: ignore[reportImplicitRelativeImport]

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.getenv("DE_E2E") != "1",
        reason="Requires PostgreSQL (set DE_E2E=1)",
    ),
]


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _service(session: AsyncSession) -> ShareService:
    return ShareService(session)


def _share_payload(*, resource_id: int, **overrides: object) -> dict[str, object]:
    stamp = _stamp()
    payload: dict[str, object] = {
        "id": stamp,
        "creator": 7,
        "time": stamp,
        "exp": None,
        "uuid": f"s{stamp}"[:16],
        "pwd": None,
        "resource_id": resource_id,
        "oid": 9,
        "type": 0,
        "auto_pwd": True,
        "ticket_require": False,
        "access_count": 0,
    }
    payload.update(overrides)
    return payload


def _ticket_payload(*, uuid: str, ticket: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": _stamp(),
        "uuid": uuid,
        "ticket": ticket,
        "exp": None,
        "args": None,
        "access_time": None,
    }
    payload.update(overrides)
    return payload


async def _cleanup(session: AsyncSession, share_ids: list[int], ticket_ids: list[int]) -> None:
    share_repo = ShareRepository(session)
    ticket_repo = ShareTicketRepository(session)
    for ticket_id in reversed(ticket_ids):
        ticket = await ticket_repo.get_by_id(ticket_id)
        if ticket is not None:
            await ticket_repo.delete(ticket)
    for share_id in reversed(share_ids):
        share = await share_repo.get_by_id(share_id)
        if share is not None:
            await share_repo.delete(share)


class TestShareServiceCoverage:
    async def test_save_creates_detail_view_get_and_proxy_share(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            created = await svc.save(
                ShareCreateRequest(
                    resource_id=resource_id,
                    exp=_now_ms() + 60_000,
                    pwd="secret-pwd",
                    uuid="CreateUuid1234",
                    oid=9,
                    type=1,
                    auto_pwd=False,
                ),
                _user(),
            )
            share_ids.append(created.id)

            detail = await svc.detail(ShareDetailRequest(resource_id=resource_id))
            view = await svc.view_detail(ShareViewDetailRequest(uuid=created.uuid))
            by_id = await svc.get_by_id(resource_id)
            proxy = await svc.proxy(created.uuid)
            resource_data = await svc.get_resource_data(created)
            status_payload = await svc.get_status(resource_id)

            assert created.resource_id == resource_id
            assert created.uuid == "CreateUuid1234"
            assert created.type == 1
            assert created.auto_pwd is False
            assert detail is not None and detail.id == created.id
            assert view is not None and view.uuid == created.uuid
            assert by_id is not None and by_id.resource_id == resource_id
            assert proxy is not None and proxy.uuid == created.uuid
            assert resource_data == {"resource_id": resource_id, "resource_type": "chart"}
            assert status_payload == {
                "uuid": created.uuid,
                "exp": created.exp,
                "has_pwd": True,
                "auto_pwd": False,
            }
            assert await svc.get_by_id(_stamp()) is None
            assert await svc.proxy(f"missing{resource_id}"[:16]) is None
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_save_updates_existing_share_and_preserves_unset_fields(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            existing = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    exp=_now_ms() + 30_000,
                    uuid="ExistingUuid123",
                    pwd="oldpwd",
                    auto_pwd=True,
                    type=0,
                    oid=3,
                )
            )
            share_ids.append(existing.id)

            updated = await svc.save(
                ShareCreateRequest(
                    resource_id=resource_id,
                    exp=_now_ms() + 90_000,
                    pwd="newpwd",
                    auto_pwd=False,
                    type=1,
                    oid=9,
                ),
                _user(),
            )

            stored = await share_repo.get_by_id(existing.id)
            assert updated.id == existing.id
            assert updated.uuid == "ExistingUuid123"
            assert updated.pwd == "newpwd"
            assert updated.auto_pwd is False
            assert updated.type == 1
            assert updated.oid == 9
            assert stored is not None and stored.creator == 7
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_delete_removes_share_and_related_tickets(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        ticket_repo = ShareTicketRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(_share_payload(resource_id=resource_id, uuid="DeleteUuid12345"))
            share_ids.append(share.id)
            ticket_one = await ticket_repo.create(_ticket_payload(uuid=share.uuid, ticket=f"ticket-{_stamp()}"))
            ticket_two = await ticket_repo.create(_ticket_payload(uuid=share.uuid, ticket=f"ticket-{_stamp()}"))
            ticket_ids.extend([ticket_one.id, ticket_two.id])

            await svc.delete(ShareDeleteRequest(resource_id=resource_id))

            assert await share_repo.get_by_id(share.id) is None
            assert await ticket_repo.get_by_id(ticket_one.id) is None
            assert await ticket_repo.get_by_id(ticket_two.id) is None
            share_ids.clear()
            ticket_ids.clear()
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_resolve_records_access_and_updates_ticket_access_time(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        ticket_repo = ShareTicketRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="ResolveUuid1234",
                    pwd="resolvepwd",
                    exp=_now_ms() + 120_000,
                    access_count=0,
                )
            )
            share_ids.append(share.id)
            ticket = await ticket_repo.create(
                _ticket_payload(uuid=share.uuid, ticket=f"resolve-ticket-{_stamp()}")
            )
            ticket_ids.append(ticket.id)

            resolved = await svc.resolve(share.uuid, "resolvepwd")
            stored_share = await share_repo.get_by_id(share.id)
            stored_ticket = await ticket_repo.get_by_id(ticket.id)

            assert resolved.uuid == share.uuid
            assert stored_share is not None and stored_share.access_count == 1
            assert stored_ticket is not None and stored_ticket.access_time is not None
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_validate_password_handles_success_and_failure_cases(
        self,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="ValidPwdUuid123",
                    pwd="pwd-123",
                    exp=_now_ms() + 120_000,
                )
            )
            share_ids.append(share.id)

            monkeypatch.setattr(
                "app.utils.rsa_utils.decrypt_rsa",
                lambda ciphertext: "ValidPwdUuid123,pwd-123" if ciphertext == "good" else "ValidPwdUuid123,bad",
            )

            assert await svc.validate_password({}) == {
                "code": 1,
                "data": None,
                "msg": "Missing ciphertext",
            }
            assert await svc.validate_password({"ciphertext": "good"}) == {
                "code": 0,
                "data": True,
                "msg": "",
            }
            assert await svc.validate_password({"ciphertext": "bad"}) == {
                "code": 1,
                "data": False,
                "msg": "Password incorrect",
            }

            monkeypatch.setattr("app.utils.rsa_utils.decrypt_rsa", lambda ciphertext: "not-a-pair")
            assert await svc.validate_password({"ciphertext": "format"}) == {
                "code": 1,
                "data": None,
                "msg": "Invalid ciphertext format",
            }

            def _raise(_: str) -> str:
                raise ValueError("boom")

            monkeypatch.setattr("app.utils.rsa_utils.decrypt_rsa", _raise)
            assert await svc.validate_password({"ciphertext": "explode"}) == {
                "code": 1,
                "data": None,
                "msg": "Decryption failed",
            }
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_validate_password_returns_share_not_found_and_expired(self, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            expired = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="ExpiredPwdUuid12",
                    pwd="expiredpwd",
                    exp=_now_ms() - 1_000,
                )
            )
            share_ids.append(expired.id)
            monkeypatch.setattr("app.utils.rsa_utils.decrypt_rsa", lambda ciphertext: "MissingUuid123456,pwd")
            assert await svc.validate_password({"ciphertext": "missing"}) == {
                "code": 1,
                "data": None,
                "msg": "Share not found",
            }

            monkeypatch.setattr("app.utils.rsa_utils.decrypt_rsa", lambda ciphertext: "ExpiredPwdUuid12,expiredpwd")
            assert await svc.validate_password({"ciphertext": "expired"}) == {
                "code": 1,
                "data": None,
                "msg": "Share has expired",
            }
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_proxy_info_validates_password_ticket_and_token_claims(
        self,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        ticket_repo = ShareTicketRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="ProxyUuid123456",
                    pwd="proxypwd",
                    exp=_now_ms() + 180_000,
                    type=1,
                )
            )
            share_ids.append(share.id)
            ticket = await ticket_repo.create(
                _ticket_payload(
                    uuid=share.uuid,
                    ticket="proxy-ticket",
                    exp=_now_ms() + 180_000,
                    args={"scope": "full", "filters": [1, 2]},
                )
            )
            ticket_ids.append(ticket.id)

            monkeypatch.setattr("app.utils.rsa_utils.decrypt_rsa", lambda ciphertext: f"{share.uuid},proxypwd")
            result = await svc.proxy_info(
                ShareProxyInfoRequest(
                    uuid=share.uuid,
                    ciphertext="ciphertext",
                    in_iframe=True,
                    ticket="proxy-ticket",
                )
            )

            assert result is not None
            response, link_token = result
            settings = get_settings()
            claims = jwt.decode(link_token, settings.share_secret_key, algorithms=[settings.jwt_algorithm])

            assert response.resource_id == str(resource_id)
            assert response.uid == "7"
            assert response.type == "dataV"
            assert response.pwd_valid is True
            assert response.in_iframe_error is True
            assert response.ticket_valid_vo.ticket_valid is True
            assert response.ticket_valid_vo.ticket_exp is False
            assert response.ticket_valid_vo.args == '{"scope": "full", "filters": [1, 2]}'
            assert claims["resourceId"] == resource_id
            assert claims["uid"] == 7
            assert claims["oid"] == 9
            assert share.exp is not None
            assert claims["exp"] <= share.exp // 1000
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_proxy_info_handles_missing_share_invalid_ticket_and_decrypt_failure(
        self,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            assert await svc.proxy_info(ShareProxyInfoRequest(uuid="missing-share")) is None

            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="ProxyBadUuid1234",
                    pwd="proxypwd",
                    exp=_now_ms() - 500,
                )
            )
            share_ids.append(share.id)

            def _raise(_: str) -> str:
                raise ValueError("decrypt failed")

            monkeypatch.setattr("app.utils.rsa_utils.decrypt_rsa", _raise)
            result = await svc.proxy_info(
                ShareProxyInfoRequest(
                    uuid=share.uuid,
                    ciphertext="bad-ciphertext",
                    ticket="missing-ticket",
                )
            )

            assert result is not None
            response, _ = result
            assert response.exp is True
            assert response.pwd_valid is False
            assert response.ticket_valid_vo.ticket_valid is False
            assert response.ticket_valid_vo.ticket_exp is False
            assert response.type == "dashboard"
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_save_ticket_create_update_and_passthrough_existing(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        ticket_repo = ShareTicketRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(_share_payload(resource_id=resource_id, uuid="TicketUuid123456"))
            share_ids.append(share.id)

            generated = await svc.save_ticket(
                ShareTicketSaveRequest(
                    uuid=share.uuid,
                    ticket=f"generated-{_stamp()}",
                    exp=_now_ms() + 60_000,
                    args={"role": "viewer"},
                    generate_new=True,
                )
            )
            ticket_ids.append(generated.id)

            created = await svc.save_ticket(
                ShareTicketSaveRequest(
                    uuid=share.uuid,
                    ticket="known-ticket",
                    exp=_now_ms() + 30_000,
                )
            )
            ticket_ids.append(created.id)

            updated = await svc.save_ticket(
                ShareTicketSaveRequest(
                    uuid=share.uuid,
                    ticket="known-ticket",
                    exp=_now_ms() + 90_000,
                    args={"step": 2},
                )
            )
            unchanged = await svc.save_ticket(
                ShareTicketSaveRequest(uuid=share.uuid, ticket="known-ticket")
            )
            stored = await ticket_repo.get_by_ticket("known-ticket")

            assert generated.uuid == share.uuid
            assert generated.args == {"role": "viewer"}
            assert created.ticket == "known-ticket"
            assert updated.args == {"step": 2}
            assert unchanged.id == updated.id
            assert stored is not None and stored.exp == updated.exp
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_delete_ticket_and_detail_tickets(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        ticket_repo = ShareTicketRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(_share_payload(resource_id=resource_id, uuid="DetailTicketUid1"))
            share_ids.append(share.id)
            ticket_a = await ticket_repo.create(_ticket_payload(uuid=share.uuid, ticket="ticket-a"))
            ticket_b = await ticket_repo.create(_ticket_payload(uuid=share.uuid, ticket="ticket-b"))
            ticket_ids.extend([ticket_a.id, ticket_b.id])

            details = await svc.detail_tickets(ShareTicketDetailRequest(uuid=share.uuid))
            await svc.delete_ticket(ShareTicketDeleteRequest(ticket="ticket-a"))

            assert {ticket.ticket for ticket in details} == {"ticket-a", "ticket-b"}
            assert await ticket_repo.get_by_id(ticket_a.id) is None
            ticket_ids.remove(ticket_a.id)
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_generate_embed_token_honors_share_expiry(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="EmbedUuid123456",
                    exp=_now_ms() + 90_000,
                )
            )
            share_ids.append(share.id)

            token = await svc.generate_embed_token(share.uuid)
            settings = get_settings()
            claims = jwt.decode(token, settings.share_secret_key, algorithms=[settings.jwt_algorithm])

            assert claims["resourceId"] == resource_id
            assert claims["uuid"] == share.uuid
            assert claims["uid"] == 7
            assert claims["oid"] == 9
            assert share.exp is not None
            assert claims["exp"] <= share.exp // 1000
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_switcher_edit_uuid_query_relation_enable_ticket_and_temp_ticket(self, db_session: AsyncSession) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        other_resource_id = resource_id + 1
        duplicate_uuid = f"D{resource_id}"[:16]
        unique_uuid = f"U{resource_id + 2}"[:16]
        try:
            created_result = await svc.switcher(resource_id, _user())
            created = created_result["data"]
            share_ids.append(created.id)
            other_share = await share_repo.create(
                _share_payload(resource_id=other_resource_id, uuid=duplicate_uuid)
            )
            share_ids.append(other_share.id)

            assert created_result["status"] == "created"
            assert len(created.pwd or "") == 4
            assert await svc.edit_uuid(resource_id, "bad!") == "链接只能包含8-16位字母和数字"
            assert await svc.edit_uuid(resource_id, duplicate_uuid) == "链接已存在"
            assert await svc.edit_uuid(resource_id + 999, unique_uuid) == "分享不存在"
            assert await svc.edit_uuid(resource_id, unique_uuid) == ""

            exp_updated = await svc.edit_exp(resource_id, 0)
            pwd_updated = await svc.edit_pwd(resource_id, "", False)
            await svc.enable_ticket(str(resource_id), True)
            rows = await svc.query_shares()
            relations = await svc.query_relation_by_user(7)
            deleted_result = await svc.switcher(resource_id, _user())
            temp_ticket = svc.generate_temp_ticket()
            stored = await share_repo.get_by_resource_id(resource_id)

            assert exp_updated is not None and exp_updated.exp is None
            assert pwd_updated is not None and pwd_updated.pwd is None and pwd_updated.auto_pwd is False
            assert any(row.resource_id == resource_id for row in rows)
            assert relations[str(other_resource_id)] == duplicate_uuid
            assert stored is None
            assert deleted_result == {"status": "deleted"}
            assert len(temp_ticket) == 8 and temp_ticket.isalnum()
            share_ids.clear()
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_proxy_info_returns_empty_link_token_when_password_wrong(
        self,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="Bug004PwdUuid12",
                    pwd="correct-pwd",
                    exp=_now_ms() + 300_000,
                )
            )
            share_ids.append(share.id)

            monkeypatch.setattr("app.utils.rsa_utils.decrypt_rsa", lambda _: "Bug004PwdUuid12,wrong-pwd")
            result = await svc.proxy_info(
                ShareProxyInfoRequest(uuid=share.uuid, ciphertext="bad")
            )
            assert result is not None
            response, link_token = result
            assert response.pwd_valid is False
            assert link_token == ""
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_proxy_info_returns_empty_link_token_when_expired(
        self,
        db_session: AsyncSession,
    ) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="Bug004ExpUuid12",
                    exp=_now_ms() - 10_000,
                )
            )
            share_ids.append(share.id)

            result = await svc.proxy_info(ShareProxyInfoRequest(uuid=share.uuid))
            assert result is not None
            response, link_token = result
            assert response.exp is True
            assert link_token == ""
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_proxy_info_returns_empty_link_token_when_ticket_required_but_invalid(
        self,
        db_session: AsyncSession,
    ) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id = _stamp()
        try:
            share = await share_repo.create(
                _share_payload(
                    resource_id=resource_id,
                    uuid="Bug004TktUuid12",
                    exp=_now_ms() + 300_000,
                    ticket_require=True,
                )
            )
            share_ids.append(share.id)

            result = await svc.proxy_info(
                ShareProxyInfoRequest(uuid=share.uuid, ticket="nonexistent-ticket")
            )
            assert result is not None
            response, link_token = result
            assert response.ticket_valid_vo.ticket_valid is False
            assert link_token == ""
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_proxy_info_rejects_ticket_with_wrong_uuid(
        self,
        db_session: AsyncSession,
    ) -> None:
        svc = _service(db_session)
        share_repo = ShareRepository(db_session)
        ticket_repo = ShareTicketRepository(db_session)
        share_ids: list[int] = []
        ticket_ids: list[int] = []
        resource_id_a = _stamp()
        resource_id_b = _stamp()
        try:
            share_a = await share_repo.create(
                _share_payload(
                    resource_id=resource_id_a,
                    uuid="ShareAuuid12345",
                    exp=_now_ms() + 300_000,
                    ticket_require=True,
                )
            )
            share_b = await share_repo.create(
                _share_payload(
                    resource_id=resource_id_b,
                    uuid="ShareBuuid12345",
                    exp=_now_ms() + 300_000,
                )
            )
            share_ids.extend([share_a.id, share_b.id])

            ticket = await ticket_repo.create(
                _ticket_payload(uuid=share_b.uuid, ticket="cross-uuid-ticket", exp=_now_ms() + 300_000)
            )
            ticket_ids.append(ticket.id)

            result = await svc.proxy_info(
                ShareProxyInfoRequest(uuid=share_a.uuid, ticket="cross-uuid-ticket")
            )
            assert result is not None
            response, link_token = result
            assert response.ticket_valid_vo.ticket_valid is False
            assert link_token == ""
        finally:
            await _cleanup(db_session, share_ids, ticket_ids)

    async def test_generate_temp_ticket_uses_secrets(self) -> None:
        ticket = ShareService.generate_temp_ticket()
        assert len(ticket) == 8
        assert ticket.isalnum()
