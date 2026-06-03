from __future__ import annotations

# pyright: reportMissingTypeArgument=false, reportAttributeAccessIssue=false

from collections.abc import Generator
from typing import cast

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.template_service import get_template_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


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

    async def find_categories(self, payload: object) -> list[dict]:
        return await self.categories()

    async def category_form(self, category_id: str) -> dict:
        return {
            "category": {"id": category_id, "name": "Default Category"},
            "templates": [{"id": "tpl_1", "name": "Template 1"}],
        }

    async def delete(self, template_id: str, category_id: str | None = None) -> None:
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

    async def find_by_body(self, payload: object) -> list[dict]:
        tid = getattr(payload, "id", None) or getattr(payload, "template_id", None)
        if tid:
            return [await self.find_one(tid)]
        return [{"id": "tpl_1", "name": "Template 1"}]

    async def list_templates(self, keyword: str | None = None) -> list[dict]:
        if keyword:
            return [{"id": "tpl_kw", "name": f"Result for {keyword}"}]
        return [
            {"id": "tpl_1", "name": "Template 1"},
            {"id": "tpl_2", "name": "Template 2"},
        ]

    async def template_list(self, payload: object) -> list[dict]:
        return await self.list_templates(getattr(payload, "keyword", None))

    async def update(self, payload: object) -> dict:
        self.updated_payloads.append(payload)
        return {
            "id": payload.id if hasattr(payload, "id") else "tpl_1",
            "name": payload.name if hasattr(payload, "name") and payload.name else "Updated",
            "templateType": "self",
        }

    async def name_check(self, payload: object) -> str:
        return "none"

    async def category_template_name_check(self, payload: object) -> str:
        return "none"

    async def delete_category(self, category_id: str) -> str:
        return "success"

    async def batch_delete(self, payload: object) -> None:
        pass

    async def batch_update(self, payload: object) -> None:
        pass

    async def find_categories_by_template_ids(self, payload: object) -> list[str]:
        return ["cat1"]

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
# Tests — existing endpoints (unchanged)
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
async def test_template_save_accepts_stringified_json_fields(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/save",
        headers=auth_headers,
        json={
            "name": "Serialized Template",
            "dvType": "dashboard",
            "templateStyle": '{"width": 1920, "height": 1080}',
            "templateData": '[{"component":"Text"}]',
            "dynamicData": '{"view-1": {"data": []}}'
        },
    )
    assert response.status_code == 200
    payload, _user = cast(tuple[object, object], fake_service.saved_templates[-1])
    assert payload.template_style == {"width": 1920, "height": 1080}
    assert payload.template_data == [{"component": "Text"}]
    assert payload.dynamic_data == {"view-1": {"data": []}}


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
        "/de2api/templateManage/delete/tpl_1/cat1",
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
    response = await client.get(
        "/de2api/templateManage/findOne/tpl_1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "tpl_1"
    assert data["name"] == "Found Template"


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
# Tests — new/changed endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_template_find_categories(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/findCategories",
        headers=auth_headers,
        json={},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert data[0]["id"] == "cat1"


@pytest.mark.asyncio
async def test_template_find_with_body(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/find",
        headers=auth_headers,
        json={"id": "tpl_1"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert data[0]["id"] == "tpl_1"


@pytest.mark.asyncio
async def test_template_template_list(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/templateList",
        headers=auth_headers,
        json={},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_template_name_check(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/nameCheck",
        headers=auth_headers,
        json={"name": "My Template"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == "none"


@pytest.mark.asyncio
async def test_category_template_name_check(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/categoryTemplateNameCheck",
        headers=auth_headers,
        json={"categoryId": "cat1"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == "none"


@pytest.mark.asyncio
async def test_delete_category(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/deleteCategory/cat1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == "success"


@pytest.mark.asyncio
async def test_batch_delete(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/batchDelete",
        headers=auth_headers,
        json={"templateIds": ["tpl_1", "tpl_2"]},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_batch_update(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/batchUpdate",
        headers=auth_headers,
        json={"templateIds": ["tpl_1"], "categories": ["cat1"]},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_find_categories_by_template_ids(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeTemplateService,
) -> None:
    response = await client.post(
        "/de2api/templateManage/findCategoriesByTemplateIds",
        headers=auth_headers,
        json={"templateIds": ["tpl_1"]},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert "cat1" in data


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
    response = await client.post("/de2api/templateManage/delete/tpl_1/cat1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_find_categories_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/templateManage/findCategories",
        json={},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_template_list_body_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/templateManage/templateList",
        json={},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_store_toggle_favorite_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/store/toggleFavorite",
        json={"resourceId": 1},
    )
    assert response.status_code == 401
