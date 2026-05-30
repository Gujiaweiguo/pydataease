from __future__ import annotations

# pyright: reportMissingImports=false

import json
import re
from typing import final

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.models.sys_variable import CoreSysVariable, CoreSysVariableValue
from app.repositories.watermark_repo import WatermarkRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.watermark import WatermarkResponse, WatermarkSaveRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.param_resolver import ParamResolver, ResolutionSource


@final
class WatermarkService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = WatermarkRepository(session)
        self.session = session
        self.param_resolver = ParamResolver()

    async def get_watermark_info(self, feature_enabled: bool = True) -> WatermarkResponse | None:
        if not feature_enabled:
            return None
        entity = await self.repo.get()
        if entity is None:
            return None
        return WatermarkResponse.model_validate(entity)

    def resolve_placeholders(self, text: str, context: dict[str, str], resolver: ParamResolver | None = None) -> str:
        if resolver is None:
            return re.sub(r"\$\{(\w+)\}", lambda match: context.get(match.group(1), ""), text)
        return self.resolve_watermark_text(text, context, resolver)

    def resolve_watermark_text(
        self,
        text: str,
        context: dict[str, str],
        resolver: ParamResolver | None = None,
    ) -> str:
        keys = list(dict.fromkeys(re.findall(r"\$\{(\w+)\}", text)))
        if not keys:
            return text
        active_resolver = resolver or self.param_resolver
        sources = [ResolutionSource(kind="embedContext", key=key, raw_value=value) for key, value in context.items()]
        resolved_map, _ = active_resolver.resolve(keys=keys, sources=sources)
        return re.sub(
            r"\$\{(\w+)\}",
            lambda match: self._stringify_resolved_value(resolved_map.get(match.group(1))),
            text,
        )

    @staticmethod
    def build_public_payload(watermark: WatermarkResponse | dict[str, object] | None) -> dict[str, object]:
        if watermark is None:
            return {"enable": False}

        setting_content: str | None
        if isinstance(watermark, dict):
            raw_setting_content = watermark.get("settingContent")
        else:
            raw_setting_content = watermark.setting_content

        setting_content = raw_setting_content if isinstance(raw_setting_content, str) else None
        if not setting_content:
            return {"enable": False}

        try:
            parsed = json.loads(setting_content)
        except json.JSONDecodeError:
            return {"enable": False}

        if not isinstance(parsed, dict):
            return {"enable": False}

        enabled = parsed.get("enable")
        if not isinstance(enabled, bool) or not enabled:
            return {"enable": False}

        return {
            "enable": True,
            "text": parsed.get("text") if isinstance(parsed.get("text"), str) else "",
            "opacity": parsed.get("opacity") if isinstance(parsed.get("opacity"), int | float) else 0,
            "fontSize": parsed.get("fontSize") if isinstance(parsed.get("fontSize"), int | float) else 0,
            "color": parsed.get("color") if isinstance(parsed.get("color"), str) else "",
        }

    async def save_watermark_info(self, payload: WatermarkSaveRequest) -> None:
        update_data: dict[str, object] = {}
        if payload.version is not None:
            update_data["version"] = payload.version
        if payload.setting_content is not None:
            update_data["setting_content"] = payload.setting_content
        if update_data:
            await self.repo.update(update_data)

    async def _system_variable_sources(self, keys: list[str], session: AsyncSession) -> list[ResolutionSource]:
        if not keys:
            return []
        stmt = (
            select(CoreSysVariable.name, CoreSysVariableValue.value)
            .outerjoin(CoreSysVariableValue, CoreSysVariableValue.variable_id == CoreSysVariable.id)
            .where(CoreSysVariable.name.in_(keys))
            .order_by(CoreSysVariable.id.asc(), CoreSysVariableValue.create_time.asc(), CoreSysVariableValue.id.asc())
        )
        result = await session.execute(stmt)
        selected_values: dict[str, str | None] = {}
        for name, value in result.all():
            if name not in selected_values:
                selected_values[name] = value
        return [
            ResolutionSource(
                kind="sysVariable",
                key=name,
                raw_value=value,
                source_meta={"variableName": name},
            )
            for name, value in selected_values.items()
        ]

    @staticmethod
    def _stringify_resolved_value(resolved: object) -> str:
        if resolved is None:
            return ""
        value = getattr(resolved, "value", None)
        if value is None:
            return ""
        return str(value)


async def get_watermark_service(session: AsyncSession = Depends(get_db)) -> WatermarkService:
    return WatermarkService(session)
