from __future__ import annotations

# pyright: reportMissingTypeArgument=false

from collections.abc import Generator
import importlib
from typing import Any, cast

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.share import ProxyInfoResponse, ShareResponse, TicketValidVO  # pyright: ignore[reportImplicitRelativeImport]
from app.services.share_service import get_share_service  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.config import get_settings  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]

jwt = importlib.import_module("jose.jwt")


class FakeShareService:
    def __init__(self) -> None:
        self.status_calls: list[int] = []
        self.deleted_tickets: list[str] = []
        self.view_detail_payloads: list[Any] = []
        self.proxy_payloads: list[Any] = []
        self.saved_shares: list[tuple[Any, Any]] = []
        self.edit_exp_calls: list[tuple[int, int]] = []
        self.edit_pwd_calls: list[tuple[int, str, bool]] = []

    async def status(self, resource_id: int) -> bool:
        self.status_calls.append(resource_id)
        return resource_id == 101

    async def get_status(self, resource_id: int) -> bool:
        return await self.status(resource_id)

    async def validate_password(self, payload: object) -> dict[str, Any]:
        return {"code": 0, "data": True, "msg": ""}

    async def proxy_info(self, payload: Any) -> tuple[ProxyInfoResponse, str] | None:
        self.proxy_payloads.append(payload)
        settings = get_settings()
        link_token = jwt.encode(
            {"uid": 7, "oid": 9, "resourceId": 100, "exp": 9999999999},
            settings.share_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        return (
            ProxyInfoResponse(
                resource_id="100",
                uid="7",
                exp=False,
                pwd_valid=True,
                type="dashboard",
                in_iframe_error=False,
                share_disable=False,
                pe_require_valid=True,
                ticket_valid_vo=TicketValidVO(),
                uuid="proxy-share-uuid",
            ),
            link_token,
        )

    async def save(self, payload: Any, user: Any) -> ShareResponse:
        self.saved_shares.append((payload, user))
        return ShareResponse(
            id=21,
            creator=getattr(user, "user_id", 0),
            time=123456,
            exp=getattr(payload, "exp", None),
            uuid=getattr(payload, "uuid", None) or "saved-share-uuid",
            pwd=getattr(payload, "pwd", None),
            resource_id=getattr(payload, "resource_id", 0),
            oid=getattr(payload, "oid", 0),
            type=getattr(payload, "type", 0),
            auto_pwd=getattr(payload, "auto_pwd", True),
            ticket_require=False,
            access_count=0,
        )

    async def detail(self, payload: Any) -> ShareResponse | None:
        return None

    async def delete(self, payload: Any) -> None:
        return None

    async def view_detail(self, payload: Any) -> ShareResponse | None:
        self.view_detail_payloads.append(payload)
        return ShareResponse(
            id=31,
            creator=7,
            time=654321,
            exp=None,
            uuid=getattr(payload, "uuid", "missing-uuid"),
            pwd=None,
            resource_id=401,
            oid=9,
            type=0,
            auto_pwd=True,
            ticket_require=False,
            access_count=0,
        )

    async def get_by_id(self, resource_id: int) -> ShareResponse | None:
        if resource_id == 999999:
            return None
        return ShareResponse(
            id=41,
            creator=7,
            time=777777,
            exp=None,
            uuid="detail-share-uuid",
            pwd=None,
            resource_id=resource_id,
            oid=9,
            type=0,
            auto_pwd=True,
            ticket_require=False,
            access_count=0,
        )

    async def proxy(self, uuid: str) -> ShareResponse | None:
        return None

    async def save_ticket(self, payload: Any) -> None:
        return None

    async def delete_ticket(self, payload: Any) -> None:
        self.deleted_tickets.append(getattr(payload, "ticket", ""))

    async def detail_tickets(self, payload: Any) -> list[Any]:
        return []

    async def resolve(self, uuid: str, password: str | None = None) -> ShareResponse:
        raise NotImplementedError

    async def generate_embed_token(self, uuid: str) -> str:
        return "unused"

    async def get_resource_data(self, share: ShareResponse) -> dict[str, Any]:
        return {"resource_id": share.resource_id}

    async def edit_exp(self, resource_id: int, exp: int) -> ShareResponse | None:
        self.edit_exp_calls.append((resource_id, exp))
        return ShareResponse(
            id=51,
            creator=7,
            time=888888,
            exp=exp,
            uuid="edit-exp-uuid",
            pwd=None,
            resource_id=resource_id,
            oid=9,
            type=0,
            auto_pwd=True,
            ticket_require=False,
            access_count=0,
        )

    async def edit_pwd(self, resource_id: int, pwd: str, auto_pwd: bool) -> ShareResponse | None:
        self.edit_pwd_calls.append((resource_id, pwd, auto_pwd))
        return ShareResponse(
            id=61,
            creator=7,
            time=999999,
            exp=None,
            uuid="edit-pwd-uuid",
            pwd=pwd or None,
            resource_id=resource_id,
            oid=9,
            type=0,
            auto_pwd=auto_pwd,
            ticket_require=False,
            access_count=0,
        )


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeShareService, None, None]:
    svc = FakeShareService()
    app.dependency_overrides[get_share_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_share_service, None)


@pytest.mark.asyncio
async def test_share_status_shared(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/status/101", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["data"] is True
    assert fake_service.status_calls == [101]


@pytest.mark.asyncio
async def test_share_status_not_shared(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/status/202", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["data"] is False
    assert fake_service.status_calls == [202]


@pytest.mark.asyncio
async def test_share_delete_ticket(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/deleteTicket",
        headers=auth_headers,
        json={"ticket": "ticket-123"},
    )

    assert response.status_code == 200
    assert response.json()["data"] is None
    assert fake_service.deleted_tickets == ["ticket-123"]


@pytest.mark.asyncio
async def test_share_view_detail(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/viewDetail",
        headers=auth_headers,
        json={"uuid": "view-share-uuid"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 31
    assert data["uuid"] == "view-share-uuid"
    assert data["resourceId"] == 401
    assert len(fake_service.view_detail_payloads) == 1
    assert getattr(fake_service.view_detail_payloads[0], "uuid") == "view-share-uuid"


@pytest.mark.asyncio
async def test_share_proxy_info_missing_uuid_returns_422(client: AsyncClient) -> None:
    response = await client.post("/de2api/share/proxyInfo", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_share_proxy_info_null_uuid_returns_422(client: AsyncClient) -> None:
    response = await client.post("/de2api/share/proxyInfo", json={"uuid": None})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_share_save_with_minimal_fields(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/save",
        headers=auth_headers,
        json={"resourceId": 305},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["resourceId"] == 305
    assert data["pwd"] is None
    assert data["exp"] is None
    assert data["autoPwd"] is True
    payload = cast(Any, fake_service.saved_shares[0][0])
    assert payload.resource_id == 305
    assert payload.pwd is None
    assert payload.exp is None
    assert payload.uuid is None
    assert payload.type == 0
    assert payload.oid == 0


@pytest.mark.asyncio
async def test_share_edit_exp_with_large_value(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    large_exp = 9223372036854775807

    response = await client.post(
        "/de2api/share/editExp",
        headers=auth_headers,
        json={"resourceId": 77, "exp": large_exp},
    )

    assert response.status_code == 200
    assert response.json()["data"]["exp"] == str(large_exp)
    assert fake_service.edit_exp_calls == [(77, large_exp)]


@pytest.mark.asyncio
async def test_share_edit_pwd_empty_password_clears_password(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/editPwd",
        headers=auth_headers,
        json={"resourceId": 88, "pwd": "", "autoPwd": False},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["pwd"] is None
    assert data["autoPwd"] is False
    assert fake_service.edit_pwd_calls == [(88, "", False)]


@pytest.mark.asyncio
async def test_share_detail_nonexistent_resource(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/detail/999999", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["data"] is None


@pytest.mark.asyncio
async def test_share_delete_ticket_empty_body_returns_422(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/de2api/share/deleteTicket",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_share_view_detail_with_wrong_field_returns_422(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/de2api/share/viewDetail",
        headers=auth_headers,
        json={"resourceId": 401},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_uncovered_share_endpoints_require_auth(client: AsyncClient) -> None:
    responses = [
        await client.get("/de2api/share/status/101"),
        await client.post("/de2api/share/deleteTicket", json={"ticket": "ticket-123"}),
        await client.post("/de2api/share/viewDetail", json={"uuid": "view-share-uuid"}),
    ]

    for response in responses:
        assert response.status_code == 401
