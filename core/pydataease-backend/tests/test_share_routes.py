from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.schemas.share import ShareResponse, ShareTicketResponse
from app.services.share_service import get_share_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class FakeShareService:
    def __init__(self) -> None:
        self.saved_shares: list[object] = []
        self.deleted_resource_ids: list[int] = []
        self.saved_tickets: list[object] = []
        self.deleted_tickets: list[str] = []

    async def get_status(self, resource_id: int) -> bool:
        return True

    async def validate_password(self, payload: object) -> dict:
        if isinstance(payload, dict) and not payload.get("resourceId"):
            return {"code": 1, "data": None, "msg": "Missing resourceId"}
        return {"status": "valid", "data": True}

    async def proxy_info(self, payload: object) -> ShareResponse | None:
        return ShareResponse(
            id=1,
            creator=7,
            time=1000000,
            exp=None,
            uuid="abc123xyz",
            pwd=None,
            resource_id=100,
            oid=1,
            type=0,
            auto_pwd=True,
            ticket_require=False,
        )

    async def save(self, payload: object, user: object) -> ShareResponse:
        self.saved_shares.append((payload, user))
        return ShareResponse(
            id=2,
            creator=user.user_id if hasattr(user, "user_id") else 0,
            time=2000000,
            exp=None,
            uuid="newshareuuid",
            pwd="secret",
            resource_id=200,
            oid=1,
            type=0,
            auto_pwd=True,
            ticket_require=False,
        )

    async def detail(self, payload: object) -> ShareResponse | None:
        return ShareResponse(
            id=3,
            creator=7,
            time=3000000,
            exp=None,
            uuid="detuuid",
            pwd=None,
            resource_id=300,
            oid=1,
            type=0,
            auto_pwd=True,
            ticket_require=False,
        )

    async def delete(self, payload: object) -> None:
        self.deleted_resource_ids.append(payload.resource_id if hasattr(payload, "resource_id") else 0)

    async def view_detail(self, payload: object) -> ShareResponse | None:
        return ShareResponse(
            id=4,
            creator=7,
            time=4000000,
            exp=None,
            uuid="viewuuid",
            pwd=None,
            resource_id=400,
            oid=1,
            type=0,
            auto_pwd=True,
            ticket_require=False,
        )

    async def get_by_id(self, resource_id: int) -> ShareResponse | None:
        return ShareResponse(
            id=5,
            creator=7,
            time=5000000,
            exp=None,
            uuid="getuuid",
            pwd=None,
            resource_id=resource_id,
            oid=1,
            type=0,
            auto_pwd=True,
            ticket_require=False,
        )

    async def proxy(self, uuid: str) -> ShareResponse | None:
        return ShareResponse(
            id=6,
            creator=7,
            time=6000000,
            exp=None,
            uuid=uuid,
            pwd=None,
            resource_id=600,
            oid=1,
            type=0,
            auto_pwd=True,
            ticket_require=False,
        )

    async def save_ticket(self, payload: object) -> ShareTicketResponse:
        self.saved_tickets.append(payload)
        return ShareTicketResponse(
            id=10,
            uuid="shareuuid",
            ticket="ticket-abc",
            exp=None,
            args=None,
            access_time=None,
        )

    async def delete_ticket(self, payload: object) -> None:
        self.deleted_tickets.append(payload.ticket if hasattr(payload, "ticket") else "")

    async def detail_tickets(self, payload: object) -> list[ShareTicketResponse]:
        return [
            ShareTicketResponse(
                id=11,
                uuid="shareuuid",
                ticket="ticket-xyz",
                exp=None,
                args=None,
                access_time=None,
            )
        ]


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
async def test_share_proxy_info(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/proxyInfo",
        json={"uuid": "abc123xyz"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 1
    assert data["uuid"] == "abc123xyz"
    assert data["resourceId"] == 100


@pytest.mark.asyncio
async def test_share_save(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/save",
        headers=auth_headers,
        json={"resourceId": 200, "autoPwd": True},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 2
    assert data["uuid"] == "newshareuuid"
    assert data["resourceId"] == 200
    assert len(fake_service.saved_shares) == 1


@pytest.mark.asyncio
async def test_share_detail(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/detail",
        headers=auth_headers,
        json={"resourceId": 300},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 3
    assert data["resourceId"] == 300


@pytest.mark.asyncio
async def test_share_delete(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/delete",
        headers=auth_headers,
        json={"resourceId": 999},
    )
    assert response.status_code == 200
    assert fake_service.deleted_resource_ids == [999]


@pytest.mark.asyncio
async def test_share_get_by_id(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.get(
        "/de2api/share/detail/500",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 5
    assert data["resourceId"] == 500


@pytest.mark.asyncio
async def test_share_save_ticket(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/saveTicket",
        headers=auth_headers,
        json={"uuid": "shareuuid", "ticket": "ticket-abc"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 10
    assert data["ticket"] == "ticket-abc"
    assert len(fake_service.saved_tickets) == 1


@pytest.mark.asyncio
async def test_share_detail_tickets(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/detailTicket",
        headers=auth_headers,
        json={"uuid": "shareuuid"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["ticket"] == "ticket-xyz"


@pytest.mark.asyncio
async def test_share_proxy(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.get(
        "/de2api/share/proxy/testuuid",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["uuid"] == "testuuid"


@pytest.mark.asyncio
async def test_share_save_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/share/save",
        json={"resourceId": 1},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_share_delete_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/share/delete",
        json={"resourceId": 1},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_share_detail_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/share/detail",
        json={"resourceId": 1},
    )
    assert response.status_code == 401
