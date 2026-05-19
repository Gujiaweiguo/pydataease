from __future__ import annotations

import base64
import json
import os
import time
from typing import Any, cast

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8100")


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


def _assert_ok(response: httpx.Response) -> dict[str, object]:
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 0, body
    assert "data" in body, body
    return body


def _data_dict(body: dict[str, object]) -> dict[str, Any]:
    data = body["data"]
    assert isinstance(data, dict), body
    return cast(dict[str, Any], data)


def _data_list(body: dict[str, object]) -> list[dict[str, Any]]:
    data = body["data"]
    assert isinstance(data, list), body
    return cast(list[dict[str, Any]], data)


def _find_node_by_id(nodes: object, target_id: int) -> dict[str, object] | None:
    if not isinstance(nodes, list):
        return None
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if str(node.get("id")) == str(target_id):
            return node
        found = _find_node_by_id(node.get("children"), target_id)
        if found is not None:
            return found
    return None


@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires running server (set DE_E2E=1)")
@pytest.mark.asyncio
async def test_e2e_dashboard_full() -> None:
    ids: dict[str, int | str] = {}
    headers: dict[str, str] = {}
    stamp = int(time.time() * 1000)
    folder_name = f"E2E Dashboard Folder {stamp}"
    dashboard_name = f"E2E Dashboard {stamp}"
    updated_dashboard_name = f"{dashboard_name} Updated"
    renamed_dashboard_name = f"{dashboard_name} Renamed"
    watermark_content = json.dumps({"type": "custom", "content": f"e2e-{stamp}", "enable": True})

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as api_client:
        try:
            # === Step 1: Login ===
            dekey_response = await api_client.get("/de2api/dekey")
            dekey_body = _assert_ok(dekey_response)
            dekey = dekey_body["data"]
            assert isinstance(dekey, str) and dekey
            login = await api_client.post(
                "/de2api/login/localLogin",
                json={"name": _encrypt("admin", dekey), "pwd": _encrypt("DataEase@123456", dekey), "origin": 0},
            )
            login_body = _assert_ok(login)
            login_data = _data_dict(login_body)
            token = login_data["token"]
            assert isinstance(token, str) and token
            headers = {"X-DE-TOKEN": token}
            print("Step 1: Login - OK")

            # === Step 2: Create Folder ===
            folder_response = await api_client.post(
                "/de2api/dataVisualization/save",
                headers=headers,
                json={"name": folder_name, "nodeType": "folder", "pid": 0, "type": "dashboard"},
            )
            folder_body = _assert_ok(folder_response)
            folder_data = _data_dict(folder_body)
            ids["folder"] = int(folder_data["id"])
            assert folder_data["name"] == folder_name
            print(f"Step 2: Create Folder - OK (id={ids['folder']})")

            # === Step 3: Create Dashboard ===
            dashboard_response = await api_client.post(
                "/de2api/dataVisualization/save",
                headers=headers,
                json={"name": dashboard_name, "nodeType": "leaf", "pid": ids["folder"], "type": "dashboard"},
            )
            dashboard_body = _assert_ok(dashboard_response)
            dashboard_data = _data_dict(dashboard_body)
            ids["dashboard"] = int(dashboard_data["id"])
            assert dashboard_data["name"] == dashboard_name
            print(f"Step 3: Create Dashboard - OK (id={ids['dashboard']})")

            # === Step 4: Tree Browse ===
            tree_response = await api_client.post(
                "/de2api/dataVisualization/tree",
                headers=headers,
                json={"busiFlag": "dashboard"},
            )
            tree_body = _assert_ok(tree_response)
            tree_node = _find_node_by_id(tree_body["data"], int(ids["dashboard"]))
            assert tree_node is not None
            assert tree_node["name"] == dashboard_name
            print(f"Step 4: Tree Browse - OK (id={ids['dashboard']})")

            # === Step 5: Find By ID ===
            find_response = await api_client.post(
                "/de2api/dataVisualization/findById",
                headers=headers,
                json={"id": ids["dashboard"], "busiFlag": "dashboard"},
            )
            find_body = _assert_ok(find_response)
            find_data = _data_dict(find_body)
            assert str(find_data["id"]) == str(ids["dashboard"])
            assert find_data["name"] == dashboard_name
            print(f"Step 5: Find By ID - OK (id={ids['dashboard']})")

            # === Step 6: Name Check ===
            name_check_new = await api_client.post(
                "/de2api/dataVisualization/nameCheck",
                headers=headers,
                json={"name": f"{dashboard_name} Unique", "pid": ids["folder"], "type": "dashboard", "nodeType": "leaf", "opt": "new"},
            )
            name_check_new_body = _assert_ok(name_check_new)
            assert name_check_new_body["data"] is True
            name_check_existing = await api_client.post(
                "/de2api/dataVisualization/nameCheck",
                headers=headers,
                json={"name": dashboard_name, "pid": ids["folder"], "type": "dashboard", "nodeType": "leaf", "opt": "new"},
            )
            name_check_existing_body = _assert_ok(name_check_existing)
            assert name_check_existing_body["data"] is False
            print(f"Step 6: Name Check - OK (id={ids['dashboard']})")

            component_data: list[dict[str, Any]] = [
                {
                    "id": "text-1",
                    "component": "VText",
                    "label": "Overview",
                    "propValue": "Revenue Overview",
                    "rect": {"x": 16, "y": 20, "w": 12, "h": 4},
                }
            ]
            canvas_style_data = {
                "width": 1920,
                "height": 1080,
                "backgroundColor": "#f5f6f7",
                "screenScale": {"x": 1, "y": 1},
            }

            # === Step 7: Save Canvas ===
            save_canvas_response = await api_client.post(
                "/de2api/dataVisualization/saveCanvas",
                headers=headers,
                json={
                    "id": ids["dashboard"],
                    "name": dashboard_name,
                    "pid": ids["folder"],
                    "type": "dashboard",
                    "componentData": json.dumps(component_data),
                    "canvasStyleData": json.dumps(canvas_style_data),
                    "canvasViewInfo": {},
                    "mobileLayout": False,
                },
            )
            save_canvas_body = _assert_ok(save_canvas_response)
            save_canvas_data = _data_dict(save_canvas_body)
            assert str(save_canvas_data["id"]) == str(ids["dashboard"])
            ids["content_id"] = str(save_canvas_data.get("contentId") or "")
            ids["check_version"] = str(save_canvas_data.get("checkVersion") or "")
            print(f"Step 7: Save Canvas - OK (id={ids['dashboard']})")

            # === Step 8: Update Canvas ===
            component_data[0]["propValue"] = "Revenue Overview Updated"
            component_data.append(
                {
                    "id": "shape-1",
                    "component": "VShape",
                    "style": {"backgroundColor": "#1890ff"},
                    "rect": {"x": 40, "y": 20, "w": 10, "h": 6},
                }
            )
            update_canvas_response = await api_client.post(
                "/de2api/dataVisualization/updateCanvas",
                headers=headers,
                json={
                    "id": ids["dashboard"],
                    "name": dashboard_name,
                    "pid": ids["folder"],
                    "type": "dashboard",
                    "componentData": json.dumps(component_data),
                    "canvasStyleData": json.dumps({**canvas_style_data, "backgroundColor": "#ffffff"}),
                    "canvasViewInfo": {},
                    "contentId": ids["content_id"],
                    "checkVersion": ids["check_version"],
                    "mobileLayout": False,
                },
            )
            update_canvas_body = _assert_ok(update_canvas_response)
            update_canvas_data = _data_dict(update_canvas_body)
            assert update_canvas_data["status"] == 2
            print(f"Step 8: Update Canvas - OK (id={ids['dashboard']})")

            # === Step 9: Update Base ===
            update_base_response = await api_client.post(
                "/de2api/dataVisualization/updateBase",
                headers=headers,
                json={"id": ids["dashboard"], "name": updated_dashboard_name, "pid": ids["folder"], "type": "dashboard", "mobileLayout": True},
            )
            update_base_body = _assert_ok(update_base_response)
            update_base_data = _data_dict(update_base_body)
            assert update_base_data["name"] == updated_dashboard_name
            print(f"Step 9: Update Base - OK (id={ids['dashboard']})")

            # === Step 10: Rename ===
            rename_response = await api_client.post(
                "/de2api/dataVisualization/reName",
                headers=headers,
                json={"id": ids["dashboard"], "name": renamed_dashboard_name},
            )
            rename_body = _assert_ok(rename_response)
            rename_data = _data_dict(rename_body)
            assert rename_data["name"] == renamed_dashboard_name
            print(f"Step 10: Rename - OK (id={ids['dashboard']})")

            # === Step 11: Find Recent ===
            recent_response = await api_client.post(
                "/de2api/dataVisualization/findRecent",
                headers=headers,
                json={"size": 10},
            )
            recent_body = _assert_ok(recent_response)
            recent_data = _data_list(recent_body)
            assert any(str(item.get("id")) == str(ids["dashboard"]) for item in recent_data)
            print(f"Step 11: Find Recent - OK (id={ids['dashboard']})")

            # === Step 12: Check Canvas Change ===
            canvas_change_response = await api_client.post(
                "/de2api/dataVisualization/checkCanvasChange",
                headers=headers,
                json={"id": ids["dashboard"], "contentId": ids["content_id"], "checkVersion": ids["check_version"]},
            )
            canvas_change_body = _assert_ok(canvas_change_response)
            assert canvas_change_body["data"] in {"NoChange", "Repeat"}
            print(f"Step 12: Check Canvas Change - OK (id={ids['dashboard']})")

            # === Step 13: Update Publish Status ===
            publish_response = await api_client.post(
                "/de2api/dataVisualization/updatePublishStatus",
                headers=headers,
                json={"id": ids["dashboard"], "status": 2, "activeViewIds": []},
            )
            publish_body = _assert_ok(publish_response)
            publish_data = _data_dict(publish_body)
            assert str(publish_data["id"]) == str(ids["dashboard"])
            assert publish_data["status"] == 2
            print(f"Step 13: Update Publish Status - OK (id={ids['dashboard']})")

            # === Step 14: View Detail List ===
            view_detail_response = await api_client.get(
                f"/de2api/dataVisualization/viewDetailList/{ids['dashboard']}",
                headers=headers,
            )
            view_detail_body = _assert_ok(view_detail_response)
            assert isinstance(view_detail_body["data"], list)
            print(f"Step 14: View Detail List - OK (id={ids['dashboard']})")

            # === Step 15: Find Copy Resource ===
            copy_resource_response = await api_client.get(
                f"/de2api/dataVisualization/findCopyResource/{ids['dashboard']}/dashboard",
                headers=headers,
            )
            copy_resource_body = _assert_ok(copy_resource_response)
            copy_resource_data = _data_dict(copy_resource_body)
            assert str(copy_resource_data["id"]) == str(ids["dashboard"])
            print(f"Step 15: Find Copy Resource - OK (id={ids['dashboard']})")

            # === Step 16: Find DV Type ===
            dv_type_response = await api_client.get(
                f"/de2api/dataVisualization/findDvType/{ids['dashboard']}",
                headers=headers,
            )
            dv_type_body = _assert_ok(dv_type_response)
            assert dv_type_body["data"] == "dashboard"
            print(f"Step 16: Find DV Type - OK (id={ids['dashboard']})")

            # === Step 17: Update Check Version ===
            version_response = await api_client.get(
                f"/de2api/dataVisualization/updateCheckVersion/{ids['dashboard']}",
                headers=headers,
            )
            version_body = _assert_ok(version_response)
            assert version_body["data"] == ""
            print(f"Step 17: Update Check Version - OK (id={ids['dashboard']})")

            # === Step 18: Favorites/Store ===
            add_store_response = await api_client.post(
                f"/de2api/store/{ids['dashboard']}",
                headers=headers,
                json={"resourceType": 0},
            )
            add_store_body = _assert_ok(add_store_response)
            assert add_store_body["data"] is not None
            favorited_response = await api_client.post(
                "/de2api/store/favorited",
                headers=headers,
                json={"resourceId": ids["dashboard"], "resourceType": 0},
            )
            favorited_body = _assert_ok(favorited_response)
            favorited_data = _data_dict(favorited_body)
            assert str(favorited_data["resourceId"]) == str(ids["dashboard"])
            assert favorited_data["favorited"] is True
            remove_store_response = await api_client.post(
                f"/de2api/store/del/{ids['dashboard']}",
                headers=headers,
                json={"resourceType": 0},
            )
            remove_store_body = _assert_ok(remove_store_response)
            assert remove_store_body["data"] is not None
            print(f"Step 18: Favorites/Store - OK (id={ids['dashboard']})")

            # === Step 19: Watermark ===
            save_watermark_response = await api_client.post(
                "/de2api/watermark/save",
                headers=headers,
                json={"settingContent": watermark_content},
            )
            _assert_ok(save_watermark_response)  # save returns data=None on success
            find_watermark_response = await api_client.get("/de2api/watermark/find", headers=headers)
            find_watermark_body = _assert_ok(find_watermark_response)
            find_watermark_data = _data_dict(find_watermark_body)
            assert "settingContent" in find_watermark_data
            print("Step 19: Watermark - OK")

            # === Step 20: Subject/Theme ===
            subject_response = await api_client.post("/de2api/visualizationSubject/query", headers=headers)
            subject_body = _assert_ok(subject_response)
            _ = _data_list(subject_body)
            print("Step 20: Subject/Theme - OK")

            # === Step 21: Background ===
            background_response = await api_client.get("/de2api/visualizationBackground/findAll", headers=headers)
            background_body = _assert_ok(background_response)
            assert isinstance(background_body["data"], (list, dict))
            print("Step 21: Background - OK")

            # === Step 22: Share ===
            share_save_response = await api_client.post(
                "/de2api/share/save",
                headers=headers,
                json={"resourceId": ids["dashboard"], "type": 0},
            )
            share_save_body = _assert_ok(share_save_response)
            share_data = _data_dict(share_save_body)
            ids["share_uuid"] = str(share_data["uuid"])
            assert str(share_data["resourceId"]) == str(ids["dashboard"])
            share_detail_response = await api_client.post(
                "/de2api/share/detail",
                headers=headers,
                json={"resourceId": ids["dashboard"]},
            )
            share_detail_body = _assert_ok(share_detail_response)
            share_detail_data = _data_dict(share_detail_body)
            assert str(share_detail_data["resourceId"]) == str(ids["dashboard"])
            share_proxy_response = await api_client.post(
                "/de2api/share/proxyInfo",
                json={"uuid": ids["share_uuid"], "inIframe": False},
            )
            share_proxy_body = _assert_ok(share_proxy_response)
            share_proxy_data = _data_dict(share_proxy_body)
            assert share_proxy_data["uuid"] == ids["share_uuid"]
            enable_ticket_response = await api_client.post(
                "/de2api/share/enableTicket",
                headers=headers,
                json={"resourceId": str(ids["dashboard"]), "require": True},
            )
            assert enable_ticket_response.status_code == 200, enable_ticket_response.text
            ticket_limit_response = await api_client.get("/de2api/share/ticketLimit", headers=headers)
            ticket_limit_body = _assert_ok(ticket_limit_response)
            assert ticket_limit_body["data"] == 0
            print(f"Step 22: Share - OK (id={ids['dashboard']})")

            # === Step 23: Linkage ===
            linkage_response = await api_client.post(
                "/de2api/linkage/getViewLinkageGather",
                headers=headers,
                json={"dvId": ids["dashboard"], "viewId": 0},
            )
            linkage_body = _assert_ok(linkage_response)
            assert isinstance(linkage_body["data"], (list, dict))
            print(f"Step 23: Linkage - OK (id={ids['dashboard']})")

            # === Step 24: Link Jump ===
            jump_response = await api_client.get(
                f"/de2api/linkJump/queryVisualizationJumpInfo/{ids['dashboard']}/core",
                headers=headers,
            )
            assert jump_response.status_code == 200, f"Link Jump failed: {jump_response.status_code}"
            jump_body = jump_response.json()
            assert isinstance(jump_body["data"], (list, dict, type(None)))
            print(f"Step 24: Link Jump - OK (id={ids['dashboard']})")

            # === Step 25: Outer Params ===
            outer_params_response = await api_client.get(
                f"/de2api/outerParams/queryWithVisualizationId/{ids['dashboard']}",
                headers=headers,
            )
            assert outer_params_response.status_code == 200, f"Outer Params failed: {outer_params_response.status_code}"
            outer_params_body = outer_params_response.json()
            assert outer_params_body["data"] is None or isinstance(outer_params_body["data"], (list, dict))
            print(f"Step 25: Outer Params - OK (id={ids['dashboard']})")

            # === Step 26: Export ===
            export_response = await api_client.post("/de2api/exportCenter/exportTasks/1", headers=headers)
            export_body = _assert_ok(export_response)
            assert isinstance(export_body["data"], list)
            print("Step 26: Export - OK")

            # === Step 27: Template ===
            template_response = await api_client.post("/de2api/templateManage/tree", headers=headers)
            template_body = _assert_ok(template_response)
            assert isinstance(template_body["data"], list)
            print("Step 27: Template - OK")

            # === Step 28: Delete Logic ===
            delete_logic_response = await api_client.post(
                f"/de2api/dataVisualization/deleteLogic/{ids['dashboard']}/dashboard",
                headers=headers,
            )
            delete_logic_body = _assert_ok(delete_logic_response)
            _ = _data_dict(delete_logic_body)
            print(f"Step 28: Delete Logic - OK (id={ids['dashboard']})")
        finally:
            # === Step 29: Cleanup ===
            if headers and ids.get("share_uuid"):
                await api_client.post(
                    "/de2api/share/delete",
                    headers=headers,
                    json={"resourceId": ids["dashboard"]},
                )
            if headers and ids.get("dashboard"):
                await api_client.post(
                    "/de2api/dataVisualization/delete",
                    headers=headers,
                    json={"id": ids["dashboard"]},
                )
            if headers and ids.get("folder"):
                await api_client.post(
                    "/de2api/dataVisualization/delete",
                    headers=headers,
                    json={"id": ids["folder"]},
                )
            print(
                f"Step 29: Cleanup - OK (dashboard={ids.get('dashboard')}, folder={ids.get('folder')}, share={ids.get('share_uuid')})"
            )
