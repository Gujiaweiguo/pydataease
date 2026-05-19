from __future__ import annotations

from collections.abc import Generator

import pytest

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.task import TaskRetryResponse, TaskStatusResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.task_service import get_task_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakeTaskService:
    def __init__(self) -> None:
        self.retried_task_ids: list[str] = []
        self.last_limit = 0

    async def get_status(self, task_id: str, user: TokenUser) -> TaskStatusResponse:
        return TaskStatusResponse(
            id=task_id,
            user_id=user.user_id if hasattr(user, "user_id") else 0,
            file_name="export.xlsx",
            export_status="RUNNING",
            export_progress="45",
            export_from=1,
            export_from_type="dataset",
            export_time=123456,
            msg=None,
            params={},
        )

    async def retry_task(self, task_id: str, user: TokenUser) -> TaskRetryResponse:
        self.retried_task_ids.append(task_id)
        return TaskRetryResponse(task_id=task_id, status="INITIATED")

    async def list_recent_tasks(self, user: TokenUser, limit: int = 20) -> list[TaskStatusResponse]:
        self.last_limit = limit
        return [
            TaskStatusResponse(
                id="task-1",
                user_id=user.user_id if hasattr(user, "user_id") else 0,
                file_name="export.xlsx",
                export_status="SUCCESS",
                export_progress="100",
                export_from=1,
                export_from_type="dataset",
                export_time=123456,
                msg="done",
                params={},
            )
        ]


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeTaskService, None, None]:
    svc = FakeTaskService()
    app.dependency_overrides[get_task_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_task_service, None)


@pytest.mark.asyncio
async def test_task_status_route(
    client,
    auth_headers: dict[str, str],
    fake_service: FakeTaskService,
) -> None:
    response = await client.get("/de2api/task/status/task-123", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "task-123"
    assert data["exportStatus"] == "RUNNING"


@pytest.mark.asyncio
async def test_task_retry_route(
    client,
    auth_headers: dict[str, str],
    fake_service: FakeTaskService,
) -> None:
    response = await client.post("/de2api/task/retry/task-123", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["taskId"] == "task-123"
    assert fake_service.retried_task_ids == ["task-123"]


@pytest.mark.asyncio
async def test_task_list_route(
    client,
    auth_headers: dict[str, str],
    fake_service: FakeTaskService,
) -> None:
    response = await client.get("/de2api/task/list?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["exportStatus"] == "SUCCESS"
    assert fake_service.last_limit == 5


@pytest.mark.asyncio
async def test_task_status_requires_auth(client) -> None:
    response = await client.get("/de2api/task/status/task-123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_task_retry_requires_auth(client) -> None:
    response = await client.post("/de2api/task/retry/task-123")
    assert response.status_code == 401
