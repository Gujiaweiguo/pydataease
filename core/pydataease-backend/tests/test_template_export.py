# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient  # pyright: ignore[reportMissingImports]

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.template_service import (  # pyright: ignore[reportImplicitRelativeImport]
    get_template_service,
)
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]

HEADERS = {"X-DE-TOKEN": _build_token(uid=1, oid=1)}


class FakeTemplateService:
    def __init__(self):
        self.exported_id = None

    async def export_template(self, template_id: str):
        self.exported_id = template_id
        if template_id == "not-found":
            from fastapi import HTTPException, status  # pyright: ignore[reportMissingImports]
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return {
            "name": "Test Template",
            "dvType": "PANEL",
            "nodeType": "template",
            "snapshot": "data:image/jpeg;base64,abc",
            "canvasStyleData": {},
            "componentData": [],
            "dynamicData": {},
            "version": 3,
        }


@pytest.mark.asyncio
async def test_export_template_success():
    fake = FakeTemplateService()
    app.dependency_overrides[get_template_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateManage/export/tpl-123", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["name"] == "Test Template"
        assert data["dvType"] == "PANEL"
        assert data["version"] == 3
        assert fake.exported_id == "tpl-123"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_export_template_not_found():
    fake = FakeTemplateService()
    app.dependency_overrides[get_template_service] = lambda: fake
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/templateManage/export/not-found", headers=HEADERS)
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
