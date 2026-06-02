# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient  # pyright: ignore[reportMissingImports]

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.template_market_service import (  # pyright: ignore[reportImplicitRelativeImport]
    get_template_market_service,
)
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakeMarketService:
    def __init__(self, templates=None, categories=None):
        self._templates = templates or []
        self._categories = categories or []

    async def search(self):
        return {
            "baseUrl": "",
            "categories": self._categories,
            "contents": self._templates,
        }

    async def search_recommend(self):
        return {
            "baseUrl": "",
            "contents": self._templates[:8],
        }

    async def search_preview(self):
        return await self.search()

    async def get_categories(self):
        return [c["label"] for c in self._categories if c.get("source") == "manage"]

    async def get_categories_object(self):
        fixed = [
            {"value": "recent", "label": "最近", "source": "public"},
            {"value": "suggest", "label": "推荐", "source": "public"},
        ]
        return fixed + self._categories


@pytest.fixture
def headers():
    return {"X-DE-TOKEN": _build_token(uid=1, oid=1)}


def _sample_template(title="Dashboard 1", dv_type="PANEL"):
    return {
        "id": "t1",
        "title": title,
        "thumbnail": "",
        "templateType": dv_type,
        "source": "manage",
        "classify": "推荐",
        "categoryNames": ["仪表板模板"],
        "metas": {"theme_repo": ""},
    }


def _sample_category(label="仪表板模板", cat_id="c1"):
    return {"label": label, "value": cat_id, "source": "manage"}


@pytest.mark.asyncio
async def test_search_returns_empty_when_no_templates(headers):
    fake = FakeMarketService()
    app.dependency_overrides[get_template_market_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateMarket/search", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["contents"] == []
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_returns_templates(headers):
    tpl = _sample_template()
    cat = _sample_category()
    fake = FakeMarketService(templates=[tpl], categories=[cat])
    app.dependency_overrides[get_template_market_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateMarket/search", headers=headers)
        data = resp.json()["data"]
        assert len(data["contents"]) == 1
        assert data["contents"][0]["title"] == "Dashboard 1"
        assert data["contents"][0]["source"] == "manage"
        assert len(data["categories"]) == 1
        assert data["categories"][0]["label"] == "仪表板模板"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_recommend_limits_to_8(headers):
    templates = [_sample_template(title=f"Tpl {i}") for i in range(10)]
    fake = FakeMarketService(templates=templates)
    app.dependency_overrides[get_template_market_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateMarket/searchRecommend", headers=headers)
        contents = resp.json()["data"]["contents"]
        assert len(contents) == 8
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_categories_object_includes_fixed_and_db(headers):
    cat = _sample_category()
    fake = FakeMarketService(categories=[cat])
    app.dependency_overrides[get_template_market_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateMarket/categoriesObject", headers=headers)
        items = resp.json()["data"]
        labels = [i["label"] for i in items]
        assert "最近" in labels
        assert "推荐" in labels
        assert "仪表板模板" in labels
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_categories_returns_manage_labels(headers):
    cat = _sample_category()
    fake = FakeMarketService(categories=[cat])
    app.dependency_overrides[get_template_market_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateMarket/categories", headers=headers)
        labels = resp.json()["data"]
        assert "仪表板模板" in labels
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_preview_same_shape_as_search(headers):
    tpl = _sample_template(title="Preview Test")
    fake = FakeMarketService(templates=[tpl], categories=[_sample_category()])
    app.dependency_overrides[get_template_market_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateMarket/searchPreview", headers=headers)
        data = resp.json()["data"]
        assert "contents" in data
        assert "categories" in data
        assert len(data["contents"]) == 1
    finally:
        app.dependency_overrides.clear()
