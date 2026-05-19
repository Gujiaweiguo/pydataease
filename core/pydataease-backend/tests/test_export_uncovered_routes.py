from __future__ import annotations

# pyright: reportMissingImports=false, reportMissingModuleSource=false

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.export import (  # pyright: ignore[reportImplicitRelativeImport]
    ExportTaskResponse,
)
from app.services.export_service import (  # pyright: ignore[reportImplicitRelativeImport]
    get_export_service,
)
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakeExportService:
    def __init__(self) -> None:
        self.deleted_task_ids: list[str] = []
        self.deleted_task_batches: list[tuple[list[str], object]] = []
        self.deleted_all_by_status_calls: list[tuple[str, list[str], object]] = []
        self.generated_download_uri_task_ids: list[str] = []
        self.retry_task_ids: list[str] = []
        self.export_limit_calls = 0
        self.list_task_records_calls: list[object] = []
        self.list_tasks_paginated_calls: list[tuple[str, int, int, object]] = []

    async def list_task_records(self, user: object) -> dict[str, int]:
        self.list_task_records_calls.append(user)
        return {"SUCCESS": 2, "FAILED": 1}

    async def list_tasks_paginated(
        self, status: str, page: int, limit: int, user: object
    ) -> dict[str, object]:
        self.list_tasks_paginated_calls.append((status, page, limit, user))
        return {
            "total": 1,
            "records": [
                ExportTaskResponse(
                    id="task-page-1",
                    user_id=getattr(user, "user_id", 0),
                    file_name="page-export.xlsx",
                    file_size=512.0,
                    file_size_unit="KB",
                    export_from=1,
                    export_status=status,
                    export_from_type="dataset",
                    export_time=1000000,
                    export_progress="100",
                    export_machine_name="test",
                    params={},
                    msg=None,
                ).model_dump(by_alias=True)
            ],
        }

    async def delete_task(self, task_id: str) -> None:
        self.deleted_task_ids.append(task_id)

    async def delete_tasks(self, ids: list[str], user: object) -> None:
        self.deleted_task_batches.append((ids, user))

    async def delete_all_by_status(
        self, status: str, ids: list[str], user: object
    ) -> None:
        self.deleted_all_by_status_calls.append((status, ids, user))

    async def generate_download_uri(self, task_id: str) -> dict[str, str]:
        self.generated_download_uri_task_ids.append(task_id)
        return {"uri": f"/de2api/exportCenter/download/{task_id}"}

    async def export_limit(self) -> bool:
        self.export_limit_calls += 1
        return True

    async def retry_task(self, task_id: str) -> dict[str, object]:
        self.retry_task_ids.append(task_id)
        return {
            "id": task_id,
            "exportStatus": "INITIATED",
            "exportProgress": "0",
        }


def _assert_wrapped_response(response_json: dict[str, object]) -> None:
    assert set(response_json.keys()) == {"code", "data", "msg"}
    assert response_json["code"] == 0
    assert response_json["msg"] == "success"


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
async def test_export_task_records(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/records",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"] == {"SUCCESS": 2, "FAILED": 1}
    assert len(fake_service.list_task_records_calls) == 1


@pytest.mark.asyncio
async def test_export_task_records_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/exportCenter/exportTasks/records")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_export_tasks_paginated(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportTasks/FAILED/2/5",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    data = body["data"]
    assert data["total"] == 1
    assert len(data["records"]) == 1
    assert data["records"][0]["id"] == "task-page-1"
    assert data["records"][0]["exportStatus"] == "FAILED"
    assert fake_service.list_tasks_paginated_calls[0][:3] == ("FAILED", 2, 5)


@pytest.mark.asyncio
async def test_delete_export_task_by_post(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/delete/task-get-delete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"] is None
    assert fake_service.deleted_task_ids == ["task-get-delete"]


@pytest.mark.asyncio
async def test_delete_export_tasks_post_accepts_list_payload(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/delete",
        headers=auth_headers,
        json=["task-1", "task-2"],
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"] is None
    assert fake_service.deleted_task_batches[0][0] == ["task-1", "task-2"]


@pytest.mark.asyncio
async def test_delete_export_tasks_post_accepts_dict_payload(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/delete",
        headers=auth_headers,
        json={"id": "task-dict-delete"},
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"] is None
    assert fake_service.deleted_task_batches[0][0] == ["task-dict-delete"]


@pytest.mark.asyncio
async def test_delete_all_export_tasks_by_status(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/deleteAll/FAILED",
        headers=auth_headers,
        json=["task-1", "task-3"],
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"] is None
    assert fake_service.deleted_all_by_status_calls[0][0] == "FAILED"
    assert fake_service.deleted_all_by_status_calls[0][1] == ["task-1", "task-3"]


@pytest.mark.asyncio
async def test_generate_download_uri(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.get(
        "/de2api/exportCenter/generateDownloadUri/task-uri",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"] == {"uri": "/de2api/exportCenter/download/task-uri"}
    assert fake_service.generated_download_uri_task_ids == ["task-uri"]


@pytest.mark.asyncio
async def test_generate_download_uri_requires_auth(client: AsyncClient) -> None:
    response = await client.get(
        "/de2api/exportCenter/generateDownloadUri/task-uri",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_limit(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/exportLimit",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"] is True
    assert fake_service.export_limit_calls == 1


@pytest.mark.asyncio
async def test_export_limit_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/exportCenter/exportLimit")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_retry_export(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeExportService,
) -> None:
    response = await client.post(
        "/de2api/exportCenter/retry/task-retry",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    _assert_wrapped_response(body)
    assert body["data"]["id"] == "task-retry"
    assert body["data"]["exportStatus"] == "INITIATED"
    assert fake_service.retry_task_ids == ["task-retry"]


@pytest.mark.asyncio
async def test_retry_export_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/exportCenter/retry/task-retry")
    assert response.status_code == 401
