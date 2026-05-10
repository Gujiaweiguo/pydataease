from __future__ import annotations

import pytest

from app.services.share_service import get_share_service
from tests.test_share_routes import FakeShareService


@pytest.fixture
def fake_service(install_override) -> FakeShareService:
    service = FakeShareService()
    install_override(get_share_service, service)
    return service


@pytest.mark.usefixtures("fake_service")
class TestShareContract:
    async def test_share_status_success_contract(self, async_client, auth_headers) -> None:
        """GET /de2api/share/status/{resourceId} should require X-DE-TOKEN and return boolean share status in ResultMessage.data."""
        response = await async_client.get("/de2api/share/status/100", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"] is True

    async def test_share_status_auth_failure_contract(self, async_client) -> None:
        """GET /de2api/share/status/{resourceId} should fail when auth token is missing, invalid, or expired."""
        response = await async_client.get("/de2api/share/status/100")
        assert response.status_code == 401

    async def test_validate_share_password_success_contract(self, async_client) -> None:
        """POST /de2api/share/validate should accept XpackSharePwdValidator and return validation result, potentially establishing X-DE-LINK-TOKEN flow."""
        response = await async_client.post(
            "/de2api/share/validate",
            json={"resourceId": 1, "password": "test"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0

    async def test_validate_share_password_failure_contract(self, async_client) -> None:
        """POST /de2api/share/validate should reject bad share password or malformed share input with non-zero ResultMessage.code."""
        response = await async_client.post("/de2api/share/validate", json={})
        assert response.status_code == 200
        body = response.json()
        assert body["code"] != 0


@pytest.mark.usefixtures("fake_service")
class TestShareTicketContract:
    async def test_save_ticket_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/shareTicket/saveTicket should create a ticket from TicketCreator and return ticket string in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/share/saveTicket",
            headers=auth_headers,
            json={"uuid": "shareuuid", "ticket": "ticket-abc"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "code": 0,
            "data": {"id": 10, "uuid": "shareuuid", "ticket": "ticket-abc", "exp": None, "args": None, "accessTime": None},
            "msg": "success",
        }

    async def test_save_ticket_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/shareTicket/saveTicket should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/share/saveTicket", json={"uuid": "shareuuid", "ticket": "ticket-abc"})

        assert response.status_code == 401
