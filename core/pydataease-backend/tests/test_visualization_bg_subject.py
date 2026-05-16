from __future__ import annotations

from collections.abc import Generator

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.services.visualization_bg_service import get_bg_service
from app.services.visualization_subject_service import get_subject_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    from datetime import UTC, datetime, timedelta

    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


# ---------------------------------------------------------------------------
# Fake services
# ---------------------------------------------------------------------------


class FakeBgService:
    async def find_all_grouped(self) -> dict:
        return {
            "default": [
                {
                    "id": "board_1",
                    "name": "边框1",
                    "classification": "default",
                    "content": "",
                    "remark": None,
                    "sort": None,
                    "uploadTime": None,
                    "baseUrl": "img/board",
                    "url": "board/board_1.svg",
                }
            ]
        }


class FakeSubjectService:
    def __init__(self) -> None:
        self.created: list[dict] = []
        self.deleted_ids: list[str] = []
        self.updated_ids: list[str] = []

    async def query(self) -> list[dict]:
        return [
            {
                "id": "subj_1",
                "name": "主题1",
                "type": "system",
                "details": {"color": "#fff"},
                "deleteFlag": False,
                "coverUrl": None,
                "createNum": 0,
                "createTime": 1000000,
                "createBy": "admin",
                "updateTime": None,
                "updateBy": None,
            }
        ]

    async def query_subject_with_group(self) -> list[list[dict]]:
        rows = await self.query()
        result: list[list[dict]] = []
        group: list[dict] = []
        for row in rows:
            group.append(row)
            if len(group) == 4:
                result.append(group)
                group = []
        if group:
            result.append(group)
        return result

    async def update_subject(self, payload, user) -> dict:
        if payload.id:
            self.updated_ids.append(payload.id)
            return {
                "id": payload.id,
                "name": payload.name or "Updated",
                "type": "system",
                "details": payload.details,
                "deleteFlag": False,
                "coverUrl": payload.cover_url,
                "createNum": 0,
                "createTime": 1000000,
                "createBy": "admin",
                "updateTime": 2000000,
                "updateBy": str(user.user_id),
            }
        else:
            data = {
                "id": "new_subj_1",
                "name": payload.name,
                "type": payload.type or "self",
                "details": payload.details,
                "deleteFlag": False,
                "coverUrl": payload.cover_url,
                "createNum": 0,
                "createTime": 1000000,
                "createBy": str(user.user_id),
                "updateTime": None,
                "updateBy": None,
            }
            self.created.append(data)
            return data

    async def delete_subject(self, subject_id: str) -> None:
        self.deleted_ids.append(subject_id)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_bg_service() -> Generator[FakeBgService, None, None]:
    svc = FakeBgService()
    app.dependency_overrides[get_bg_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_bg_service, None)


@pytest.fixture
def fake_subject_service() -> Generator[FakeSubjectService, None, None]:
    svc = FakeSubjectService()
    app.dependency_overrides[get_subject_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_subject_service, None)


# ---------------------------------------------------------------------------
# Background tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_bg_find_all(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_bg_service: FakeBgService,
) -> None:
    response = await client.get(
        "/de2api/visualizationBackground/findAll",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, dict)
    assert "default" in data
    assert data["default"][0]["id"] == "board_1"


@pytest.mark.asyncio
async def test_bg_find_all_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/de2api/visualizationBackground/findAll")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Subject tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_subject_query(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_subject_service: FakeSubjectService,
) -> None:
    response = await client.post(
        "/de2api/visualizationSubject/query",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "subj_1"


@pytest.mark.asyncio
async def test_subject_query_with_group(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_subject_service: FakeSubjectService,
) -> None:
    response = await client.post(
        "/de2api/visualizationSubject/querySubjectWithGroup",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    # One subject -> one group of 1
    assert len(data) == 1
    assert len(data[0]) == 1
    assert data[0][0]["id"] == "subj_1"


@pytest.mark.asyncio
async def test_subject_update_create(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_subject_service: FakeSubjectService,
) -> None:
    response = await client.post(
        "/de2api/visualizationSubject/update",
        headers=auth_headers,
        json={"name": "新主题", "type": "self", "details": {"bg": "#000"}},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "new_subj_1"
    assert data["name"] == "新主题"
    assert len(fake_subject_service.created) == 1


@pytest.mark.asyncio
async def test_subject_update_existing(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_subject_service: FakeSubjectService,
) -> None:
    response = await client.post(
        "/de2api/visualizationSubject/update",
        headers=auth_headers,
        json={"id": "subj_1", "name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "subj_1"
    assert data["name"] == "Updated Name"
    assert fake_subject_service.updated_ids == ["subj_1"]


@pytest.mark.asyncio
async def test_subject_delete(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_subject_service: FakeSubjectService,
) -> None:
    response = await client.post(
        "/de2api/visualizationSubject/delete/subj_1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert fake_subject_service.deleted_ids == ["subj_1"]


@pytest.mark.asyncio
async def test_subject_query_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/visualizationSubject/query")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_subject_update_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/visualizationSubject/update",
        json={"name": "test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_subject_delete_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/visualizationSubject/delete/subj_1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_subject_query_with_group_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/visualizationSubject/querySubjectWithGroup"
    )
    assert response.status_code == 401
