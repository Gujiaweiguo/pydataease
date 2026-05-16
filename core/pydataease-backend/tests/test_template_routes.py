from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.services.template_service import get_template_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------


class FakeTemplateService:
    def __init__(self) -> None:
        self.saved_templates: list[object] = []
        self.deleted_ids: list[str] = []
        self.updated_payloads: list[object] = []
        self.favorites: list[dict] = []
        self.toggle_calls: list[tuple[int, int, int]] = []

    async def tree(self) -> list[dict]:
        return [
            {
                "id": "cat1",
                "name": "Default",
                "pid": "0",
                "level": 0,
                "dvType": "dashboard",
                "nodeType": "folder",
                "createTime": None,
                "templateType": "system",
                "children": [],
            }
        ]

    async def save(self, payload: object, user: object) -> dict:
        self.saved_templates.append((payload, user))
        return {
            "id": "tpl_100",
            "name": payload.name if hasattr(payload, "name") else "test",
            "pid": "0",
            "level": 0,
            "dvType": "dashboard",
            "nodeType": "panel",
            "createBy": str(user.user_id) if hasattr(user, "user_id") else "0",
            "createTime": 1000000,
            "snapshot": None,
            "templateType": "self",
            "templateStyle": None,
            "templateData": None,
            "dynamicData": None,
        }

    async def name_list(self) -> list[dict]:
        return [{"id": "tpl_1", "name": "Template 1"}, {"id": "tpl_2", "name": "Template 2"}]

    async def categories(self) -> list[dict]:
        return [
            {
                "id": "cat1",
                "name": "Default",
                "pid": "0",
                "level": 0,
                "dvType": "dashboard",
                "nodeType": "folder",
                "children": [],
            }
        ]

    async def category_form(self, category_id: str) -> dict:
        return {
            "category": {"id": category_id, "name": "Default Category"},
            "templates": [{"id": "tpl_1", "name": "Template 1"}],
        }

    async def delete(self, template_id: str) -> None:
        self.deleted_ids.append(template_id)

    async def find_one(self, template_id: str) -> dict:
        return {
            "id": template_id,
            "name": "Found Template",
            "pid": "0",
            "level": 0,
            "dvType": "dashboard",
            "nodeType": "panel",
            "templateType": "self",
        }

    async def find(self, template_id: str) -> dict:
        return await self.find_one(template_id)

    async def list_templates(self, keyword: str | None = None) -> list[dict]:
        if keyword:
            return [{"id": "tpl_kw", "name": f"Result for {keyword}"}]
        return [
            {"id": "tpl_1", "name": "Template 1"},
            {"id": "tpl_2", "name": "Template 2"},
        ]

    async def update(self, payload: object) -> dict:
        self.updated_payloads.append(payload)
        return {
            "id": payload.id if hasattr(payload, "id") else "tpl_1",
            "name": payload.name if hasattr(payload, "name") and payload.name else "Updated",
            "templateType": "self",
        }

    async def check_category_template(self, category_id: str) -> bool:
        return category_id == "cat1"

    async def toggle_favorite(self, resource_id: int, uid: int, resource_type: int = 0) -> dict:
        self.toggle_calls.append((resource_id, uid, resource_type))
        return {"favorited": True}

    async def list_favorites(self, uid: int) -> list[dict]:
        return [
            {"id": 100, "resourceId": 200, "uid": uid, "resourceType": 0, "time": 1000000}
        ]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeTemplateService, None, None]:
    svc = FakeTemplateService()
    app.dependency_overrides[get_template_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_template_service, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_template_tree(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post("/de2api/templateManage/tree", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert data[0]["id"] == "cat1"


@pytest.mark.asyncio
async def test_template_save(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/save",
        headers=auth_headers,
        json={"name": "My Template", "dvType": "dashboard"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "tpl_100"
    assert len(fake_service.saved_templates) == 1


@pytest.mark.asyncio
async def test_template_name_list(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post("/de2api/templateManage/nameList", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert data[0]["id"] == "tpl_1"


@pytest.mark.asyncio
async def test_template_categories(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post("/de2api/templateManage/categories", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data[0]["id"] == "cat1"


@pytest.mark.asyncio
async def test_template_category_form(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/categoryForm",
        headers=auth_headers,
        json={"categoryId": "cat1"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["category"]["id"] == "cat1"
    assert len(data["templates"]) == 1


@pytest.mark.asyncio
async def test_template_delete(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/delete/tpl_1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert fake_service.deleted_ids == ["tpl_1"]


@pytest.mark.asyncio
async def test_template_find_one(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/findOne/tpl_1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "tpl_1"
    assert data["name"] == "Found Template"


@pytest.mark.asyncio
async def test_template_find(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/find/tpl_1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "tpl_1"


@pytest.mark.asyncio
async def test_template_list(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/list",
        headers=auth_headers,
        json={"keyword": "test"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == "tpl_kw"


@pytest.mark.asyncio
async def test_template_update(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/update",
        headers=auth_headers,
        json={"id": "tpl_1", "name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "tpl_1"
    assert len(fake_service.updated_payloads) == 1


@pytest.mark.asyncio
async def test_check_category_template(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/checkCategoryTemplate/cat1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data is True


@pytest.mark.asyncio
async def test_store_toggle_favorite(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/store/toggleFavorite",
        headers=auth_headers,
        json={"resourceId": 200, "resourceType": 0},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["favorited"] is True
    assert len(fake_service.toggle_calls) == 1


@pytest.mark.asyncio
async def test_store_list_favorites(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/store/list",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["resourceId"] == 200


# ---------------------------------------------------------------------------
# Auth gate tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_template_tree_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/templateManage/tree")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_template_save_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/templateManage/save",
        json={"name": "test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_template_delete_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/templateManage/delete/tpl_1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_store_toggle_favorite_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/store/toggleFavorite",
        json={"resourceId": 1},
    )
    assert response.status_code == 401
