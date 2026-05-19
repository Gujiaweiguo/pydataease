"""Tests for the 9 new share management + ticket endpoints."""
from __future__ import annotations

# pyright: reportMissingTypeArgument=false

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.share import ShareResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.share_service import get_share_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


# ---------------------------------------------------------------------------
# Fake service that tracks new method calls
# ---------------------------------------------------------------------------


class FakeShareManagementService:
    """Extends the pattern from test_share_routes with new methods."""

    def __init__(self) -> None:
        self.switcher_calls: list[tuple[int, object]] = []
        self.edit_exp_calls: list[tuple[int, int]] = []
        self.edit_pwd_calls: list[tuple[int, str, bool]] = []
        self.edit_uuid_calls: list[tuple[int, str]] = []
        self.query_shares_called = False
        self.relation_queries: list[int] = []
        self.enable_ticket_calls: list[tuple[str, bool]] = []
        self.temp_ticket_called = False

    # -- existing methods (minimal stubs) --

    async def get_status(self, resource_id: int) -> dict:
        return {"uuid": "abc", "exp": None, "has_pwd": False, "auto_pwd": True}

    async def validate_password(self, payload: object) -> dict:
        return {"code": 0, "data": True, "msg": ""}

    async def proxy_info(self, payload: object) -> None:
        return None

    async def save(self, payload: object, user: object) -> ShareResponse:
        rid = getattr(payload, "resource_id", 0)
        return ShareResponse(
            id=1, creator=7, time=1000, exp=None, uuid="newuuid",
            pwd=None, resource_id=rid, oid=1, type=0,
            auto_pwd=True, ticket_require=False, access_count=0,
        )

    async def detail(self, payload: object) -> None:
        return None

    async def delete(self, payload: object) -> None:
        pass

    async def view_detail(self, payload: object) -> None:
        return None

    async def get_by_id(self, resource_id: int) -> None:
        return None

    async def proxy(self, uuid: str) -> None:
        return None

    async def resolve(self, uuid: str, password: str | None = None) -> None:
        return None

    async def save_ticket(self, payload: object) -> None:
        return None

    async def delete_ticket(self, payload: object) -> None:
        pass

    async def detail_tickets(self, payload: object) -> list:
        return []

    async def generate_embed_token(self, uuid: str) -> str:
        return "fake-token"

    async def get_resource_data(self, share: object) -> dict:
        return {}

    # -- new management methods --

    async def switcher(self, resource_id: int, user: object) -> dict:
        self.switcher_calls.append((resource_id, user))
        return {"status": "created", "data": {"uuid": "switcheduuid"}}

    async def edit_exp(self, resource_id: int, exp: int) -> ShareResponse | None:
        self.edit_exp_calls.append((resource_id, exp))
        return ShareResponse(
            id=10, creator=7, time=2000, exp=exp if exp > 0 else None,
            uuid="expuuid", pwd=None, resource_id=resource_id, oid=1, type=0,
            auto_pwd=True, ticket_require=False, access_count=0,
        )

    async def edit_pwd(self, resource_id: int, pwd: str, auto_pwd: bool) -> ShareResponse | None:
        self.edit_pwd_calls.append((resource_id, pwd, auto_pwd))
        return ShareResponse(
            id=11, creator=7, time=3000, exp=None,
            uuid="pwduuid", pwd=pwd or None, resource_id=resource_id, oid=1, type=0,
            auto_pwd=auto_pwd, ticket_require=False, access_count=0,
        )

    async def edit_uuid(self, resource_id: int, uuid: str) -> str:
        self.edit_uuid_calls.append((resource_id, uuid))
        if not uuid.isalnum() or len(uuid) < 8 or len(uuid) > 16:
            return "链接只能包含8-16位字母和数字"
        return ""

    async def query_shares(self) -> list[ShareResponse]:
        self.query_shares_called = True
        return [
            ShareResponse(
                id=20, creator=7, time=4000, exp=None, uuid="q1",
                pwd=None, resource_id=100, oid=1, type=0,
                auto_pwd=True, ticket_require=False, access_count=0,
            ),
        ]

    async def query_relation_by_user(self, uid: int) -> dict[str, str]:
        self.relation_queries.append(uid)
        return {"100": "uuid100", "200": "uuid200"}

    async def enable_ticket(self, resource_id: str, require: bool) -> None:
        self.enable_ticket_calls.append((resource_id, require))

    @staticmethod
    def generate_temp_ticket() -> str:
        return "tempTicket123"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeShareManagementService, None, None]:
    svc = FakeShareManagementService()
    app.dependency_overrides[get_share_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_share_service, None)


# ---------------------------------------------------------------------------
# 1. POST /share/switcher/{resource_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_switcher_creates_share(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/switcher/42",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "created"
    assert len(fake_service.switcher_calls) == 1
    assert fake_service.switcher_calls[0][0] == 42


@pytest.mark.asyncio
async def test_switcher_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/share/switcher/42")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# 2. POST /share/editExp
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_edit_exp(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/editExp",
        headers=auth_headers,
        json={"resourceId": 55, "exp": 1700000000000},
    )
    assert response.status_code == 200
    assert len(fake_service.edit_exp_calls) == 1
    assert fake_service.edit_exp_calls[0] == (55, 1700000000000)


@pytest.mark.asyncio
async def test_edit_exp_zero_clears_expiry(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/editExp",
        headers=auth_headers,
        json={"resourceId": 55, "exp": 0},
    )
    assert response.status_code == 200
    assert fake_service.edit_exp_calls[0] == (55, 0)


# ---------------------------------------------------------------------------
# 3. POST /share/editPwd
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_edit_pwd(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/editPwd",
        headers=auth_headers,
        json={"resourceId": 77, "pwd": "newpass", "autoPwd": False},
    )
    assert response.status_code == 200
    assert fake_service.edit_pwd_calls[0] == (77, "newpass", False)


# ---------------------------------------------------------------------------
# 4. POST /share/editUuid
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_edit_uuid_success(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/editUuid",
        headers=auth_headers,
        json={"resourceId": 88, "uuid": "validNewUuid"},
    )
    assert response.status_code == 200
    # Empty string returned on success (wrapped by ResultMessage)
    assert response.json()["data"] == ""


@pytest.mark.asyncio
async def test_edit_uuid_invalid_format(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/editUuid",
        headers=auth_headers,
        json={"resourceId": 88, "uuid": "bad!"},
    )
    assert response.status_code == 200
    assert "字母和数字" in response.json()["data"]


# ---------------------------------------------------------------------------
# 5. POST /share/query
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_shares(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/query",
        headers=auth_headers,
        json={},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["uuid"] == "q1"
    assert fake_service.query_shares_called


# ---------------------------------------------------------------------------
# 6. GET /share/queryRelationByUserId/{uid}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_relation_by_user_id(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.get(
        "/de2api/share/queryRelationByUserId/7",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == {"100": "uuid100", "200": "uuid200"}
    assert fake_service.relation_queries == [7]


# ---------------------------------------------------------------------------
# 7. POST /share/enableTicket
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_enable_ticket(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareManagementService,
) -> None:
    response = await client.post(
        "/de2api/share/enableTicket",
        headers=auth_headers,
        json={"resourceId": "99", "require": True},
    )
    assert response.status_code == 200
    assert fake_service.enable_ticket_calls == [("99", True)]


# ---------------------------------------------------------------------------
# 8. GET /share/tempTicket
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_temp_ticket(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/de2api/share/tempTicket",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, str)
    assert len(data) == 8
    assert data.isalnum()


# ---------------------------------------------------------------------------
# 9. GET /share/ticketLimit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ticket_limit(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/de2api/share/ticketLimit",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"] == 0


# ---------------------------------------------------------------------------
# Auth required for all new endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_new_endpoints_require_auth(client: AsyncClient) -> None:
    """All new management endpoints should return 401 without auth."""
    endpoints = [
        ("POST", "/de2api/share/switcher/1"),
        ("POST", "/de2api/share/editExp"),
        ("POST", "/de2api/share/editPwd"),
        ("POST", "/de2api/share/editUuid"),
        ("POST", "/de2api/share/query"),
        ("GET", "/de2api/share/queryRelationByUserId/1"),
        ("POST", "/de2api/share/enableTicket"),
        ("GET", "/de2api/share/tempTicket"),
        ("GET", "/de2api/share/ticketLimit"),
    ]
    for method, url in endpoints:
        if method == "POST":
            resp = await client.post(url, json={})
        else:
            resp = await client.get(url)
        assert resp.status_code == 401, f"{method} {url} should require auth"
