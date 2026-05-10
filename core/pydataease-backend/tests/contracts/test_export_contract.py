from __future__ import annotations

import pytest

from app.services.export_service import get_export_service
from tests.test_export_routes import FakeExportService


@pytest.fixture
def fake_service(install_override) -> FakeExportService:
    service = FakeExportService()
    install_override(get_export_service, service)
    return service


@pytest.mark.usefixtures("fake_service")
class TestExportCenterContract:
    async def test_export_tasks_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/exportCenter/exportTasks/{status}/{goPage}/{pageSize} should return paged ExportTaskDTO records in ResultMessage.data."""
        response = await async_client.post("/de2api/exportCenter/exportTasks/1", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"][0]["id"] == "task-1"

    async def test_export_tasks_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/exportCenter/exportTasks/{status}/{goPage}/{pageSize} should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/exportCenter/exportTasks/1")

        assert response.status_code == 401

    async def test_download_success_contract(self, async_client) -> None:
        """GET /de2api/exportCenter/download/{id} should return blob/file payload for existing export task when authorized."""
        response = await async_client.get("/de2api/exportCenter/download/task-1")

        assert response.status_code == 200
        assert response.json() == {
            "code": 0,
            "data": {"id": "task-1", "status": "SUCCESS", "msg": "Download stub - not implemented"},
            "msg": "success",
        }

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_retry_success_contract(self) -> None:
        """POST /de2api/exportCenter/retry/{id} should resubmit a failed export task and return success ResultMessage."""
