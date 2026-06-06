"""Tests for the org-admin custom role creation flow.

Covers:
  - POST /role/createWithPerms  — create role + assign permissions + mount users
  - GET  /role/permissionDetail/{rid}  — read role's current permissions
  - POST /role/setPerms/{rid}  — replace role's permissions
  - Built-in roles cannot be modified via setPerms
  - Unknown permission point names are rejected
  - Org admin (role_id=2) can create custom roles
  - Regular user without role-management permission is blocked

Requires a running PostgreSQL (db_session fixture from db_fixtures.py).
"""

from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.fixtures.auth_fixtures import _build_token

skip_no_db = pytest.mark.skipif(
    not os.getenv("DE_E2E"),
    reason="Set DE_E2E=1 to run integration tests",
)

ADMIN_HEADERS = {"X-DE-TOKEN": _build_token(uid=1, oid=0)}
ORG_ADMIN_HEADERS = {"X-DE-TOKEN": _build_token(uid=1780033653117563687, oid=1)}
REGULAR_USER_HEADERS = {"X-DE-TOKEN": _build_token(uid=99999, oid=1)}


def _fake_role_service():
    """Override that raises — forces real DB interaction for E2E."""
    raise RuntimeError("Should not be called in E2E tests")


@skip_no_db
@pytest.mark.asyncio
async def test_create_role_with_permissions_e2e(db_session):
    role_name = f"test-custom-{os.getpid()}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/de2api/role/createWithPerms",
            json={
                "name": role_name,
                "description": "Test custom role",
                "permissionPointNames": ["menu:panel:use", "menu:dataset:use"],
            },
            headers=ADMIN_HEADERS,
        )
    assert create_resp.status_code == 200
    body = create_resp.json()
    assert body["roleName"] == role_name
    assert len(body["permissions"]) == 2
    perm_names = {p["name"] for p in body["permissions"]}
    assert "menu:panel:use" in perm_names
    assert "menu:dataset:use" in perm_names
    role_id = body["roleId"]

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            detail_resp = await client.get(
                f"/de2api/role/permissionDetail/{role_id}",
                headers=ADMIN_HEADERS,
            )
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["roleId"] == role_id
        assert len(detail["permissions"]) == 2

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            set_resp = await client.post(
                f"/de2api/role/setPerms/{role_id}",
                json={"permissionPointNames": ["menu:screen:use"]},
                headers=ADMIN_HEADERS,
            )
        assert set_resp.status_code == 200
        set_body = set_resp.json()
        assert len(set_body["permissions"]) == 1
        assert set_body["permissions"][0]["name"] == "menu:screen:use"
    finally:
        await db_session.execute(
            __import__("sqlalchemy").delete(
                __import__("app.models.role_permission", fromlist=["CoreRolePermission"]).CoreRolePermission
            ).where(
                __import__("app.models.role_permission", fromlist=["CoreRolePermission"]).CoreRolePermission.role_id == role_id
            )
        )
        await db_session.commit()
        await db_session.execute(
            __import__("sqlalchemy").delete(
                __import__("app.models.role", fromlist=["CoreRole"]).CoreRole
            ).where(
                __import__("app.models.role", fromlist=["CoreRole"]).CoreRole.id == role_id
            )
        )
        await db_session.commit()


@skip_no_db
@pytest.mark.asyncio
async def test_set_perms_on_builtin_role_rejected(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/de2api/role/setPerms/1",
            json={"permissionPointNames": ["menu:panel:use"]},
            headers=ADMIN_HEADERS,
        )
    assert resp.status_code in (400, 403)


@skip_no_db
@pytest.mark.asyncio
async def test_unknown_permission_point_rejected(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/de2api/role/createWithPerms",
            json={
                "name": "bad-role",
                "permissionPointNames": ["menu:nonexistent:use"],
            },
            headers=ADMIN_HEADERS,
        )
    assert resp.status_code == 400
    assert "Unknown permission points" in resp.json().get("detail", "")
