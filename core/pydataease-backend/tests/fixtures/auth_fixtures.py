from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt  # pyright: ignore[reportMissingImports, reportMissingModuleSource]

from app.settings.config import get_settings  # pyright: ignore[reportImplicitRelativeImport]


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
