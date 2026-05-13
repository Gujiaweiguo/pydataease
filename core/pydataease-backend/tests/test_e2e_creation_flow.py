from __future__ import annotations

import base64
import json
from collections.abc import AsyncIterator

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding


BASE_URL = "http://localhost:8100"


def _extract_public_key_pem(dekey: str) -> str:
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


def _encrypt(value: str, dekey: str) -> str:
    public_key_pem = _extract_public_key_pem(dekey)
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    assert isinstance(public_key, rsa.RSAPublicKey)
    ciphertext = public_key.encrypt(value.encode("utf-8"), padding.PKCS1v15())
    return base64.b64encode(ciphertext).decode("utf-8")


@pytest.fixture
async def api_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        yield client


@pytest.mark.asyncio
async def test_e2e_creation_flow(api_client: httpx.AsyncClient) -> None:
    ids: dict[str, int] = {}
    headers: dict[str, str] = {}

    try:
        dekey = (await api_client.get("/de2api/dekey")).json()["data"]
        login = await api_client.post(
            "/de2api/login/localLogin",
            json={"name": _encrypt("admin", dekey), "pwd": _encrypt("DataEase@123456", dekey), "origin": 0},
        )
        assert login.status_code == 200
        headers = {"X-DE-TOKEN": login.json()["data"]["token"]}

        datasource = await api_client.post(
            "/de2api/datasource/save",
            headers=headers,
            json={
                "name": "E2E Test PostgreSQL",
                "type": "postgresql",
                "pid": 0,
                "configuration": {
                    "host": "172.17.0.1",
                    "port": "5432",
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
        assert datasource.status_code == 200
        ids["datasource"] = int(datasource.json()["data"]["id"])

        tables = (await api_client.get(f"/de2api/datasource/getSchema/{ids['datasource']}", headers=headers)).json()["data"]
        preferred_tables = ["core_user", "core_menu", "core_datasource", "core_chart_view"]
        table_name = next((name for name in preferred_tables if any(item["name"] == name for item in tables)), next(item["name"] for item in tables if item["name"] not in {"alembic_version"}))
        table_fields = (await api_client.get(f"/de2api/datasource/getTableField/{ids['datasource']}/{table_name}", headers=headers)).json()["data"]
        assert table_fields

        dataset = await api_client.post(
            "/de2api/datasetTree/create",
            headers=headers,
            json={
                "name": "E2E Test Dataset",
                "nodeType": "dataset",
                "pid": 0,
                "type": "0",
                "info": {"datasourceId": ids["datasource"], "table": table_name},
                "union": [],
                "allFields": [],
            },
        )
        assert dataset.status_code == 200
        ids["dataset"] = int(dataset.json()["data"]["id"])

        dataset_details = await api_client.post(f"/de2api/datasetTree/details/{ids['dataset']}", headers=headers)
        assert dataset_details.status_code == 200
        assert dataset_details.json()["data"]["id"] == str(ids["dataset"])

        dashboard = await api_client.post(
            "/de2api/dataVisualization/save",
            headers=headers,
            json={"name": "E2E Test Dashboard", "nodeType": "dashboard", "pid": 0, "type": "dashboard"},
        )
        assert dashboard.status_code == 200
        ids["dashboard"] = int(dashboard.json()["data"]["id"])

        chart_payload = {
            "title": "E2E Test Chart",
            "sceneId": ids["dashboard"],
            "tableId": ids["dataset"],
            "type": "bar",
            "chartType": "bar",
            "render": "antv",
            "xAxis": [
                {
                    "id": table_fields[0]["name"],
                    "name": table_fields[0]["name"],
                    "dataeaseName": table_fields[0]["name"],
                    "summary": "none",
                }
            ],
            "yAxis": [],
            "viewFields": [{"id": table_fields[0]["name"], "name": table_fields[0]["name"], "dataeaseName": table_fields[0]["name"]}],
            "customAttr": {},
            "customStyle": {},
        }
        chart = await api_client.post("/de2api/chart/save", headers=headers, json=chart_payload)
        assert chart.status_code == 200
        ids["chart"] = int(chart.json()["data"]["id"])

        chart_data = await api_client.post(
            "/de2api/chart/getData",
            headers=headers,
            json={"id": ids["chart"], "xAxis": chart_payload["xAxis"], "tableId": ids["dataset"]},
        )
        assert chart_data.status_code == 200
        assert chart_data.json()["data"]["data"]

        canvas = await api_client.post(
            "/de2api/dataVisualization/saveCanvas",
            headers=headers,
            json={
                "id": ids["dashboard"],
                "name": "E2E Test Dashboard",
                "pid": 0,
                "type": "dashboard",
                "componentData": json.dumps([
                    {"id": "chart-1", "component": "VChart", "datasetId": str(ids["dataset"]), "viewId": str(ids["chart"])},
                ]),
                "canvasStyleData": json.dumps({"width": 1920, "height": 1080}),
                "canvasViewInfo": {
                    str(ids["chart"]): {
                        "id": ids["chart"],
                        "title": "E2E Test Chart",
                        "sceneId": ids["dashboard"],
                        "tableId": ids["dataset"],
                        "type": "bar",
                        "chartType": "bar",
                        "render": "antv",
                        "xAxis": chart_payload["xAxis"],
                        "yAxis": [],
                        "viewFields": chart_payload["viewFields"],
                        "customAttr": {},
                        "customStyle": {},
                    }
                },
            },
        )
        assert canvas.status_code == 200

        dashboard_detail = await api_client.post(
            "/de2api/dataVisualization/findById",
            headers=headers,
            json={"id": ids["dashboard"], "busiFlag": "dataV"},
        )
        assert dashboard_detail.status_code == 200
        dashboard_data = dashboard_detail.json()["data"]
        assert dashboard_data["componentData"]
        assert str(ids["chart"]) in dashboard_data["canvasViewInfo"]
        assert dashboard_data["canvasViewInfo"][str(ids["chart"])]

    finally:
        if ids.get("chart"):
            await api_client.post(f"/de2api/chart/del/{ids['chart']}", headers=headers)
        if ids.get("dashboard"):
            await api_client.post("/de2api/dataVisualization/delete", headers=headers, json={"id": ids["dashboard"]})
        if ids.get("dataset"):
            await api_client.post(f"/de2api/datasetTree/delete/{ids['dataset']}", headers=headers)
        if ids.get("datasource"):
            await api_client.post(f"/de2api/datasource/delete/{ids['datasource']}", headers=headers)
