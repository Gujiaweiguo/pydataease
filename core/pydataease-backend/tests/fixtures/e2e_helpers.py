"""Shared e2e test helpers — eliminates duplication across e2e test files."""
from __future__ import annotations

import base64
import os
import time
from collections.abc import AsyncIterator
from typing import Any, cast

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8100")
E2E_GATE = pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires running server (set DE_E2E=1)")


def extract_public_key_pem(dekey: str) -> str:
    """Extract RSA public key PEM from encrypted dekey string."""
    separator = base64.urlsafe_b64encode(b"-pk_separator-").decode("utf-8")
    k1, k2 = dekey.split(separator)
    ct = base64.b64decode(k1)
    cipher = Cipher(algorithms.AES(k2.encode("utf-8")), modes.CBC(b"0000000000000000"))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")
    if plaintext.startswith("-----BEGIN PUBLIC KEY-----"):
        return plaintext
    der_bytes = base64.b64decode(plaintext)
    pub = serialization.load_der_public_key(der_bytes)
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def encrypt(value: str, dekey: str) -> str:
    """RSA-encrypt a value using the dekey public key."""
    public_key_pem = extract_public_key_pem(dekey)
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    assert isinstance(public_key, rsa.RSAPublicKey)
    ciphertext = public_key.encrypt(value.encode("utf-8"), padding.PKCS1v15())
    return base64.b64encode(ciphertext).decode("utf-8")


def assert_ok(response: httpx.Response) -> dict[str, object]:
    """Assert response is 200 with code==0, return body."""
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 0, body
    assert "data" in body, body
    return body


def data_dict(body: dict[str, object]) -> dict[str, Any]:
    data = body["data"]
    assert isinstance(data, dict), body
    return cast(dict[str, Any], data)


def data_list(body: dict[str, object]) -> list[dict[str, Any]]:
    data = body["data"]
    assert isinstance(data, list), body
    return cast(list[dict[str, Any]], data)


def find_node_by_id(nodes: object, target_id: int) -> dict[str, object] | None:
    if not isinstance(nodes, list):
        return None
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if str(node.get("id")) == str(target_id):
            return node
        found = find_node_by_id(node.get("children"), target_id)
        if found is not None:
            return found
    return None


def find_component_by_id(components: object, target_id: str) -> dict[str, Any] | None:
    if not isinstance(components, list):
        return None
    for comp in components:
        if not isinstance(comp, dict):
            continue
        if comp.get("id") == target_id:
            return cast(dict[str, Any], comp)
        prop_value = comp.get("propValue")
        if isinstance(prop_value, list):
            nested = find_component_by_id(prop_value, target_id)
            if nested is not None:
                return nested
            for item in prop_value:
                if isinstance(item, dict):
                    nested = find_component_by_id(item.get("componentData"), target_id)
                    if nested is not None:
                        return nested
    return None


def ns_id() -> int:
    """Generate unique ID via time.time_ns()."""
    return int(time.time_ns())


async def login(client: httpx.AsyncClient) -> dict[str, str]:
    """Login and return auth headers dict."""
    dekey_resp = await client.get("/de2api/dekey")
    dekey_body = assert_ok(dekey_resp)
    dekey = dekey_body["data"]
    assert isinstance(dekey, str) and dekey
    password = os.environ.get("E2E_PASSWORD", "DataEase@123456")
    login_resp = await client.post(
        "/de2api/login/localLogin",
        json={"name": encrypt("admin", dekey), "pwd": encrypt(password, dekey), "origin": 0},
    )
    login_body = assert_ok(login_resp)
    login_data = data_dict(login_body)
    token = login_data["token"]
    assert isinstance(token, str) and token
    return {"X-DE-TOKEN": token}


async def create_datasource(
    client: httpx.AsyncClient, headers: dict[str, str]
) -> tuple[int, str, list[dict[str, Any]]]:
    """Create PostgreSQL datasource, discover table+fields. Returns (ds_id, table_name, table_fields)."""
    stamp = int(time.time() * 1000)
    ds_resp = await client.post(
        "/de2api/datasource/save",
        headers=headers,
        json={
            "name": f"E2E DS {stamp}",
            "type": "postgresql",
            "pid": 0,
            "configuration": {
                "host": os.environ.get("E2E_PG_HOST", "172.17.0.1"),
                "port": os.environ.get("E2E_PG_PORT", "5432"),
                "username": "dataease",
                "password": "dataease",
                "dataBase": "dataease",
                "schema": "public",
                "connectionType": "jdbc",
                "urlType": "host",
                "jdbcUrl": "",
                "extraParams": "",
                "authMethod": "",
                "initialPoolSize": "5",
                "minPoolSize": "5",
                "maxPoolSize": "50",
                "queryTimeout": "30",
            },
        },
    )
    ds_body = assert_ok(ds_resp)
    ds_id = int(data_dict(ds_body)["id"])

    tables_resp = await client.get(f"/de2api/datasource/getSchema/{ds_id}", headers=headers)
    tables = data_list(assert_ok(tables_resp))
    preferred = ["core_chart_view", "core_user", "core_menu", "core_datasource"]
    table_name = next(
        (t["name"] for t in tables if t["name"] in preferred),
        next(t["name"] for t in tables if t["name"] != "alembic_version"),
    )

    fields_resp = await client.get(f"/de2api/datasource/getTableField/{ds_id}/{table_name}", headers=headers)
    table_fields = data_list(assert_ok(fields_resp))
    assert table_fields

    return ds_id, table_name, table_fields


async def create_dataset(client: httpx.AsyncClient, headers: dict[str, str], ds_id: int, table_name: str) -> int:
    """Create dataset from datasource table. Returns dataset_id."""
    stamp = int(time.time() * 1000)
    ds_resp = await client.post(
        "/de2api/datasetTree/create",
        headers=headers,
        json={
            "name": f"E2E Dataset {stamp}",
            "nodeType": "dataset",
            "pid": 0,
            "type": "0",
            "info": {"datasourceId": ds_id, "table": table_name},
            "union": [],
            "allFields": [],
        },
    )
    return int(data_dict(assert_ok(ds_resp))["id"])


async def create_dashboard(client: httpx.AsyncClient, headers: dict[str, str], pid: int = 0) -> int:
    """Create empty dashboard. Returns dashboard_id."""
    stamp = int(time.time() * 1000)
    resp = await client.post(
        "/de2api/dataVisualization/save",
        headers=headers,
        json={"name": f"E2E Dashboard {stamp}", "nodeType": "leaf", "pid": pid, "type": "dashboard"},
    )
    return int(data_dict(assert_ok(resp))["id"])


@pytest.fixture
async def e2e_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        yield client
