from __future__ import annotations

import os
import time
import uuid
from typing import final

from fastapi import Depends, UploadFile
from sqlalchemy import desc, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.font import CoreFont
from app.utils.id_utils import _sid

FontPayload = dict[str, str | bool | float | None]

FONT_PATH = os.environ.get("DE_FONT_PATH", "/opt/dataease2.0/data/font/")


def _fallback_font() -> list[FontPayload]:
    return [
        {
            "id": "1",
            "name": "PingFang",
            "fileName": None,
            "fileTransName": None,
            "isDefault": True,
            "isBuiltin": True,
            "size": None,
            "sizeType": None,
        }
    ]


@final
class FontService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_fonts(self) -> list[FontPayload]:
        try:
            stmt = select(CoreFont).order_by(desc(CoreFont.is_default), desc(CoreFont.update_time), CoreFont.name.asc())
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
        except (AttributeError, TypeError, SQLAlchemyError, Exception):
            return _fallback_font()

        if not rows:
            return _fallback_font()
        return [self._to_dict(row) for row in rows]

    async def default_fonts(self) -> list[FontPayload]:
        fonts = await self.list_fonts()
        default_fonts = [font for font in fonts if font.get("isDefault")]
        return default_fonts or fonts[:1]

    async def create_font(self, data: FontPayload) -> None:
        try:
            name = data.get("name")
            if name:
                existing = await self.session.execute(
                    select(CoreFont).where(CoreFont.name == name)
                )
                if existing.scalars().first() is not None:
                    return

            font = CoreFont(
                id=time.time_ns(),
                name=data.get("name", ""),
                file_name=data.get("fileName"),
                file_trans_name=data.get("fileTransName"),
                is_default=data.get("isDefault", False),
                update_time=time.time_ns(),
                is_builtin=data.get("isBuiltin", False),
                size=data.get("size"),
                size_type=data.get("sizeType"),
            )
            self.session.add(font)
            await self.session.commit()
        except (AttributeError, TypeError, SQLAlchemyError, Exception):
            pass

    async def edit_font(self, data: FontPayload) -> None:
        try:
            font_id = data.get("id")
            if not font_id:
                await self.create_font(data)
                return

            if data.get("isDefault"):
                await self.session.execute(
                    update(CoreFont).values(is_default=False)
                )

            stmt = select(CoreFont).where(CoreFont.id == int(font_id))
            result = await self.session.execute(stmt)
            font = result.scalars().first()
            if font is None:
                return

            if "name" in data and data["name"] is not None:
                font.name = data["name"]
            if "fileName" in data:
                font.file_name = data["fileName"]
            if "fileTransName" in data:
                font.file_trans_name = data["fileTransName"]
            if "isDefault" in data:
                font.is_default = data["isDefault"]
            if "isBuiltin" in data:
                font.is_builtin = data["isBuiltin"]
            if "size" in data:
                font.size = data["size"]
            if "sizeType" in data:
                font.size_type = data["sizeType"]
            font.update_time = time.time_ns()

            await self.session.commit()
        except (AttributeError, TypeError, SQLAlchemyError, Exception):
            pass

    async def delete_font(self, font_id: int) -> None:
        try:
            stmt = select(CoreFont).where(CoreFont.id == font_id)
            result = await self.session.execute(stmt)
            font = result.scalars().first()
            if font is None:
                return

            file_trans_name = font.file_trans_name
            await self.session.delete(font)
            await self.session.commit()

            if file_trans_name:
                file_path = os.path.join(FONT_PATH, file_trans_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except (AttributeError, TypeError, SQLAlchemyError, Exception):
            pass

    async def upload_file(self, file: UploadFile) -> dict[str, str | float | None]:
        filename = file.filename or "unknown.ttf"
        if not filename.lower().endswith(".ttf"):
            return {}

        os.makedirs(FONT_PATH, exist_ok=True)

        ext = os.path.splitext(filename)[1]
        file_trans_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(FONT_PATH, file_trans_name)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        file_size = len(content)
        size, size_type = _human_size(file_size)
        name = os.path.splitext(filename)[0]

        return {
            "fileTransName": file_trans_name,
            "size": size,
            "sizeType": size_type,
            "name": name,
        }

    @staticmethod
    def _to_dict(row: CoreFont) -> FontPayload:
        return {
            "id": _sid(row.id),
            "name": row.name,
            "fileName": row.file_name,
            "fileTransName": row.file_trans_name,
            "isDefault": bool(row.is_default),
            "isBuiltin": bool(row.is_builtin),
            "size": row.size,
            "sizeType": row.size_type,
        }


def _human_size(byte_count: int) -> tuple[float, str]:
    if byte_count >= 1024 * 1024 * 1024:
        return round(byte_count / (1024 * 1024 * 1024), 2), "GB"
    if byte_count >= 1024 * 1024:
        return round(byte_count / (1024 * 1024), 2), "MB"
    return round(byte_count / 1024, 2), "KB"


async def get_font_service(session: AsyncSession = Depends(get_db)) -> FontService:
    return FontService(session)
