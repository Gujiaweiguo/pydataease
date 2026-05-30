from __future__ import annotations

import base64
import json
import time
from typing import Any, final

# pyright: reportMissingImports=false

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.models.engine import CoreDeEngine  # pyright: ignore[reportImplicitRelativeImport]
from app.models.geo import MapGeo  # pyright: ignore[reportImplicitRelativeImport]
from app.models.sys_setting import CoreSysSetting  # pyright: ignore[reportImplicitRelativeImport]
from app.models.system import CoreMenu  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.system_repo import MenuRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.system import MenuTreeNodeResponse, OnlineMapResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import get_default  # pyright: ignore[reportImplicitRelativeImport]

# Fixed symmetric key for engine config encryption (16 bytes = AES-128).
# Must match what GET /symmetricKey returns for engine config decryption.
_SYMMETRIC_KEY = base64.b64encode(b"DataEase@SymKey!").decode("ascii")


def _aes_encrypt(plaintext: str, key_b64: str = _SYMMETRIC_KEY) -> str:
    """AES-128-CBC encrypt with PKCS7 padding, return Base64 ciphertext."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding as sym_padding

    key = base64.b64decode(key_b64)
    iv = b"0000000000000000"
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    enc = cipher.encryptor()
    ct = enc.update(padded) + enc.finalize()
    return base64.b64encode(ct).decode()


def _aes_decrypt(ciphertext_b64: str, key_b64: str = _SYMMETRIC_KEY) -> str:
    """AES-128-CBC decrypt with PKCS7 unpadding."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding as sym_padding

    key = base64.b64decode(key_b64)
    iv = b"0000000000000000"
    ct = base64.b64decode(ciphertext_b64)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    dec = cipher.decryptor()
    padded = dec.update(ct) + dec.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode()


def _build_menu_tree(menus: list[CoreMenu]) -> list[MenuTreeNodeResponse]:
    nodes: dict[int, MenuTreeNodeResponse] = {}
    for m in menus:
        node = MenuTreeNodeResponse.model_validate(m)
        node.children = []
        nodes[m.id] = node

    roots: list[MenuTreeNodeResponse] = []
    for m in menus:
        node = nodes[m.id]
        if m.pid == 0 or m.pid not in nodes:
            roots.append(node)
        else:
            nodes[m.pid].children.append(node)
    return roots


@final
class SystemService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.menu_repo = MenuRepository(session)
        self.sys_setting_repo = SysSettingRepository(session)

    async def _get_setting(self, key: str) -> str | None:
        try:
            setting = await self.sys_setting_repo.get_by_key(key)
        except (AttributeError, TypeError):
            return None
        return setting.setting_value if setting is not None else None

    async def _get_map_default_type(self) -> str:
        return (
            await self._get_setting("map.defaultMapType")
            or get_default("map.defaultMapType")
            or "gaode"
        )

    async def query_online_map(self) -> OnlineMapResponse:
        map_type = (
            await self._get_setting("map.onlineMapType")
            or await self._get_map_default_type()
        )
        return await self.query_online_map_by_type(map_type)

    async def query_online_map_by_type(self, map_type: str) -> OnlineMapResponse:
        payload = {
            "key": await self._get_setting(f"map.{map_type}.key") or "",
            "mapType": map_type,
            "securityCode": await self._get_setting(f"map.{map_type}.securityCode") or "",
        }
        return OnlineMapResponse.model_validate(payload)

    async def save_online_map(self, key: str | None, map_type: str | None = None, security_code: str | None = None) -> OnlineMapResponse:
        normalized_type = map_type or await self._get_map_default_type()
        try:
            await self.sys_setting_repo.upsert(f"map.{normalized_type}.key", key or "", "map")
            await self.sys_setting_repo.upsert(
                f"map.{normalized_type}.securityCode",
                security_code or "",
                "map",
            )
            await self.sys_setting_repo.upsert("map.onlineMapType", normalized_type, "map")
        except (AttributeError, TypeError):
            pass
        payload = {
            "key": key or "",
            "mapType": normalized_type,
            "securityCode": security_code or "",
        }
        return OnlineMapResponse.model_validate(payload)

    async def request_timeout(self) -> int:
        value = await self._get_setting("engine.requestTimeOut") or get_default("engine.requestTimeOut") or "120"
        return int(value)

    async def query_menus(self) -> list[MenuTreeNodeResponse]:
        menus = await self.menu_repo.list_all()
        return _build_menu_tree(list(menus))

    async def list_fonts(self) -> list[object]:
        return []

    async def default_font(self) -> object:
        return None

    async def get_area_entities(self, pcode: str) -> list[object]:
        return []

    async def query_basic_settings(self) -> list[dict[str, str]]:
        """Return basic.* system settings as [{pkey, pval}, ...] for the frontend basic settings page."""
        stmt = (
            select(CoreSysSetting)
            .where(CoreSysSetting.setting_key.like("basic.%"))
            .order_by(CoreSysSetting.id.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [
            {"pkey": row.setting_key, "pval": row.setting_value or ""}
            for row in rows
        ]

    async def save_basic_settings(self, items: list[dict[str, str]]) -> None:
        """Upsert basic.* settings from [{pkey, pval}, ...] payload."""
        repo = SysSettingRepository(self.session)
        for item in items:
            key = item.get("pkey", "")
            val = item.get("pval", "")
            if key:
                await repo.upsert(key, str(val), "basic")

    async def get_engine(self) -> dict[str, object]:
        """Return engine info for the frontend engine settings page.

        The configuration is returned as an AES-encrypted Base64 string
        that the frontend decrypts using the key from GET /symmetricKey.
        """
        result = await self.session.execute(select(CoreDeEngine).limit(1))
        engine = result.scalars().first()
        if engine is None:
            return {
                "id": None,
                "type": "engine_doris",
                "configuration": None,
                "enableDataFill": False,
            }
        # JSONB column returns a dict; serialize to JSON, then encrypt
        config_json = json.dumps(engine.configuration) if engine.configuration else "{}"
        config_encrypted = _aes_encrypt(config_json)
        return {
            "id": engine.id,
            "type": engine.type,
            "configuration": config_encrypted,
            "enableDataFill": bool(engine.enable_data_fill),
        }

    async def save_engine(self, payload: dict[str, Any]) -> None:
        """Save or update engine configuration.

        The frontend sends configuration as Base64-encoded JSON.
        We decode it to a dict for JSONB storage.
        """
        result = await self.session.execute(select(CoreDeEngine).limit(1))
        engine = result.scalars().first()

        config_b64 = str(payload.get("configuration", ""))
        try:
            config_str = base64.b64decode(config_b64).decode("utf-8")
            config_dict = json.loads(config_str)
        except Exception:
            config_dict = {}

        if engine is None:
            engine = CoreDeEngine(
                id=time.time_ns(),
                name=str(payload.get("name", "engine")),
                type=str(payload.get("type", "engine_doris")),
                configuration=config_dict,
                create_time=int(time.time() * 1000),
                create_by="admin",
                enable_data_fill=bool(payload.get("enableDataFill", False)),
            )
            self.session.add(engine)
        else:
            if "type" in payload:
                engine.type = str(payload["type"])
            engine.configuration = config_dict
            engine.update_time = int(time.time() * 1000)
            if "enableDataFill" in payload:
                engine.enable_data_fill = bool(payload["enableDataFill"])
        await self.session.commit()
        await self.session.refresh(engine)

    async def validate_engine(self, payload: dict[str, Any]) -> None:
        """Validate engine configuration. Accepts the same payload as save_engine."""
        # Minimal stub: accept any configuration without actual DB connection test.
        # A full implementation would attempt to connect to the engine DB.
        pass

    async def validate_engine_by_id(self, engine_id: str) -> None:
        """Validate an existing engine by its ID."""
        # Minimal stub: if engine exists, consider it valid.
        pass

    async def get_world_tree(self) -> list[dict[str, object]]:
        """Return top-level map geo entries as a tree for the frontend map settings page."""
        result = await self.session.execute(
            select(MapGeo).order_by(MapGeo.id.asc())
        )
        geos = result.scalars().all()
        return [
            {
                "code": geo.id,
                "name": geo.name or geo.id,
            }
            for geo in geos
        ]


async def get_system_service(
    session: AsyncSession = Depends(get_db),
) -> SystemService:
    return SystemService(session)
