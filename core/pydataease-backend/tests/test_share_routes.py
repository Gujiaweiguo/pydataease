from __future__ import annotations

# pyright: reportMissingTypeArgument=false, reportAttributeAccessIssue=false, reportMissingImports=false

from collections.abc import Generator

import pytest
from httpx import AsyncClient
from jose import jwt  # pyright: ignore[reportMissingImports, reportMissingModuleSource]

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.share import ProxyInfoResponse, ShareProxyInfoRequest, ShareResponse, ShareTicketResponse, TicketValidVO  # pyright: ignore[reportImplicitRelativeImport]
from app.services.share_service import get_share_service  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.config import get_settings  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


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

    async def proxy_info(self, payload: object) -> tuple[ProxyInfoResponse, str] | None:
        settings = get_settings()
        link_token = jwt.encode(
            {"uid": 7, "oid": 1, "resourceId": 100, "exp": 9999999999},
            settings.share_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        in_iframe = False
        if isinstance(payload, ShareProxyInfoRequest):
            in_iframe = bool(payload.in_iframe)
        proxy_resp = ProxyInfoResponse(
            resource_id="100",
            uid="7",
            exp=False,
            pwd_valid=True,
            type="dashboard",
            in_iframe_error=in_iframe,
            share_disable=False,
            pe_require_valid=True,
            ticket_valid_vo=TicketValidVO(),
            uuid="abc123xyz",
        )
        return proxy_resp, link_token

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
            access_count=0,
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
            access_count=0,
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
            access_count=0,
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
            access_count=0,
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
            access_count=0,
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

    async def resolve(self, uuid: str, password: str | None = None) -> ShareResponse:
        from fastapi import HTTPException, status

        if uuid == "expired-share":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Share has expired")
        if uuid == "nonexistent":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
        if uuid == "pwd-protected":
            if not password or password != "correctpwd":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Password incorrect")
        return ShareResponse(
            id=100,
            creator=7,
            time=7000000,
            exp=None,
            uuid=uuid,
            pwd="correctpwd" if uuid == "pwd-protected" else None,
            resource_id=700,
            oid=1,
            type=0,
            auto_pwd=True,
            ticket_require=False,
            access_count=0,
        )

    async def generate_embed_token(self, uuid: str) -> str:
        from fastapi import HTTPException, status

        if uuid == "expired-share":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Share has expired")
        if uuid == "nonexistent":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
        settings = get_settings()
        claims = {"resourceId": 700, "uuid": uuid, "uid": 7, "oid": 1, "exp": 9999999999}
        return jwt.encode(claims, settings.share_secret_key, algorithm=settings.jwt_algorithm)

    async def get_resource_data(self, share: ShareResponse) -> dict:
        resource_type = "dashboard" if share.type == 0 else "chart"
        return {"resource_id": share.resource_id, "resource_type": resource_type}


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
    assert data["resourceId"] == "100"
    assert data["uid"] == "7"
    assert data["uuid"] == "abc123xyz"
    assert data["exp"] is False
    assert data["pwdValid"] is True
    assert data["type"] == "dashboard"
    assert data["inIframeError"] is False
    assert data["shareDisable"] is False
    assert data["peRequireValid"] is True
    assert data["ticketValidVO"]["ticketValid"] is True
    assert data["ticketValidVO"]["ticketExp"] is False
    assert data["ticketValidVO"]["args"] is None
    # Verify x-de-link-token header
    assert "x-de-link-token" in response.headers
    link_token = response.headers["x-de-link-token"]
    settings = get_settings()
    claims = jwt.decode(link_token, settings.share_secret_key, algorithms=[settings.jwt_algorithm])
    assert claims["uid"] == 7
    assert claims["oid"] == 1
    assert claims["resourceId"] == 100


@pytest.mark.asyncio
async def test_share_proxy_info_in_iframe(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    """Test proxyInfo with inIframe=true sets inIframeError."""
    response = await client.post(
        "/de2api/share/proxyInfo",
        json={"uuid": "abc123xyz", "inIframe": True},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["inIframeError"] is True


@pytest.mark.asyncio
async def test_share_proxy_info_link_token_is_valid_jwt(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    """Verify the link token is a valid JWT with expected claims structure."""
    response = await client.post(
        "/de2api/share/proxyInfo",
        json={"uuid": "abc123xyz"},
    )
    assert response.status_code == 200
    link_token = response.headers["x-de-link-token"]
    settings = get_settings()
    claims = jwt.decode(link_token, settings.share_secret_key, algorithms=[settings.jwt_algorithm])
    # Link token should NOT have 'uuid' claim (unlike embed token)
    assert "uuid" not in claims
    assert "uid" in claims
    assert "oid" in claims
    assert "resourceId" in claims
    assert "exp" in claims


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


# ---------------------------------------------------------------------------
# 5.1 — resolve() tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_share_not_found(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/view/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_resolve_expired_share_rejected(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/view/expired-share")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_resolve_password_protected_wrong_password(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/view/pwd-protected?password=wrongpwd")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_resolve_password_protected_correct_password(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/view/pwd-protected?password=correctpwd")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["share"]["uuid"] == "pwd-protected"
    assert data["share"]["resourceId"] == 700


@pytest.mark.asyncio
async def test_resolve_no_password_share(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    response = await client.get("/de2api/share/view/someshare")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["share"]["uuid"] == "someshare"


# ---------------------------------------------------------------------------
# 5.2 — Embed token tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_token_generation(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/embedToken",
        headers=auth_headers,
        json={"uuid": "valid-share"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "token" in data
    assert isinstance(data["token"], str)
    # Decode and verify claims
    settings = get_settings()
    claims = jwt.decode(data["token"], settings.share_secret_key, algorithms=[settings.jwt_algorithm])
    assert claims["uuid"] == "valid-share"
    assert claims["resourceId"] == 700


@pytest.mark.asyncio
async def test_embed_token_expired_share(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/embedToken",
        headers=auth_headers,
        json={"uuid": "expired-share"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_embed_token_not_found_share(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeShareService,
) -> None:
    response = await client.post(
        "/de2api/share/embedToken",
        headers=auth_headers,
        json={"uuid": "nonexistent"},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 5.3 — Public /share/view/{uuid} endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_public_view_unauthenticated(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    """Public /share/view/{uuid} should work without any auth token."""
    response = await client.get("/de2api/share/view/someshare")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["share"]["uuid"] == "someshare"
    assert data["resource"]["resource_type"] == "dashboard"


@pytest.mark.asyncio
async def test_public_view_password_prompt(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    """Password-protected share should reject without password, accept with correct password."""
    response_no_pwd = await client.get("/de2api/share/view/pwd-protected")
    assert response_no_pwd.status_code == 403

    response_with_pwd = await client.get("/de2api/share/view/pwd-protected?password=correctpwd")
    assert response_with_pwd.status_code == 200


@pytest.mark.asyncio
async def test_public_view_expired_share(
    client: AsyncClient,
    fake_service: FakeShareService,
) -> None:
    """Expired share should return 400 error."""
    response = await client.get("/de2api/share/view/expired-share")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 5.4 — RSA password decryption unit test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_proxy_info_rsa_password_decryption() -> None:
    """Verify proxy_info decrypts RSA ciphertext containing 'uuid,password'."""
    from unittest.mock import AsyncMock, MagicMock, patch

    from app.models.share import XpackShare  # pyright: ignore[reportImplicitRelativeImport]
    from app.schemas.share import ShareProxyInfoRequest  # pyright: ignore[reportImplicitRelativeImport]
    from app.services.share_service import ShareService  # pyright: ignore[reportImplicitRelativeImport]

    # Create a mock share with a known password
    mock_share = MagicMock(spec=XpackShare)
    mock_share.pwd = "mysecretpwd"
    mock_share.exp = None
    mock_share.type = 0
    mock_share.creator = 7
    mock_share.oid = 1
    mock_share.resource_id = 100
    mock_share.uuid = "testuuid"

    mock_session = AsyncMock()
    svc = ShareService(mock_session)

    with patch.object(svc.share_repo, "get_by_uuid", return_value=mock_share):
        with patch("app.utils.rsa_utils.decrypt_rsa", return_value="testuuid,mysecretpwd"):
            payload = ShareProxyInfoRequest(uuid="testuuid", ciphertext="fake_rsa_ciphertext")
            result = await svc.proxy_info(payload)
            assert result is not None
            response, _link_token = result
            assert response.pwd_valid is True

        # Test wrong password via RSA decryption
        with patch("app.utils.rsa_utils.decrypt_rsa", return_value="testuuid,wrongpwd"):
            payload = ShareProxyInfoRequest(uuid="testuuid", ciphertext="fake_rsa_ciphertext")
            result = await svc.proxy_info(payload)
            assert result is not None
            response, _link_token = result
            assert response.pwd_valid is False

        # Test decryption failure (exception) → pwd_valid = False
        with patch("app.utils.rsa_utils.decrypt_rsa", side_effect=Exception("decryption error")):
            payload = ShareProxyInfoRequest(uuid="testuuid", ciphertext="bad_ciphertext")
            result = await svc.proxy_info(payload)
            assert result is not None
            response, _link_token = result
            assert response.pwd_valid is False
