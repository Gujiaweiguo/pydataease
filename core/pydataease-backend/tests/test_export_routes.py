from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.schemas.export import ExportTaskResponse
from app.services.export_service import get_export_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class FakeExportService:
    def __init__(self) -> None:
        self.created_tasks: list[object] = []
        self.deleted_task_ids: list[str] = []
        self.deleted_all_from: list[int] = []

    async def list_tasks(
        self, export_from: int, user: object
    ) -> list[ExportTaskResponse]:
        return [
            ExportTaskResponse(
                id="task-1",
                user_id=user.user_id if hasattr(user, "user_id") else 0,
                file_name="export.xlsx",
                file_size=1024.0,
                file_size_unit="KB",
                export_from=export_from,
                export_status="SUCCESS",
                export_from_type="dataset",
                export_time=1000000,
                export_progress="100",
                export_machine_name="test",
                params={},
                msg=None,
            )
        ]

    async def create_task(
        self, payload: object, user: object
    ) -> ExportTaskResponse:
        self.created_tasks.append((payload, user))
        return ExportTaskResponse(
            id="new-task-id",
            user_id=user.user_id if hasattr(user, "user_id") else 0,
            file_name="export.xlsx",
            file_size=None,
            file_size_unit=None,
            export_from=payload.export_from if hasattr(payload, "export_from") else None,
            export_status="INITIATED",
            export_from_type=payload.export_from_type if hasattr(payload, "export_from_type") else None,
            export_time=2000000,
            export_progress="0",
            export_machine_name=None,
            params=payload.params if hasattr(payload, "params") else {},
            msg=None,
        )

    async def delete_task(self, task_id: str) -> None:
        self.deleted_task_ids.append(task_id)

    async def delete_all(self, export_from: int, user: object) -> None:
        self.deleted_all_from.append(export_from)

    async def download(self, task_id: str) -> dict[str, object]:
        return {
            "id": task_id,
            "status": "SUCCESS",
            "msg": "Download stub - not implemented",
        }

    async def retry_task(self, task_id: str) -> dict:
        return {"id": task_id, "status": "RETRYING"}


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeExportService, None, None]:
    svc = FakeExportService()
    app.dependency_overrides[get_export_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_export_service, None)


@pytest.mark.asyncio
async def test_export_list_tasks(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == "task-1"
    assert data[0]["exportStatus"] == "SUCCESS"


@pytest.mark.asyncio
async def test_export_create_task(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/create",
        headers=auth_headers,
        json={"exportFrom": 1, "exportFromType": "dataset", "params": {}},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "new-task-id"
    assert data["exportStatus"] == "INITIATED"
    assert len(fake_service.created_tasks) == 1


@pytest.mark.asyncio
async def test_export_delete_task(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/1/delete",
        headers=auth_headers,
        json={"id": "task-to-delete"},
    )
    assert response.status_code == 200
    assert fake_service.deleted_task_ids == ["task-to-delete"]


@pytest.mark.asyncio
async def test_export_delete_all(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/1/deleteAll",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert fake_service.deleted_all_from == [1]


@pytest.mark.asyncio
async def test_export_download(
    client: AsyncClient,
    fake_service: FakeExportService,
) -> None:
    response = await client.get(
        "/de2api/exportCenter/download/task-1",
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "task-1"
    assert data["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_export_create_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/create",
        json={"exportFrom": 1, "params": {}},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_list_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/1",
    )
    assert response.status_code == 401
