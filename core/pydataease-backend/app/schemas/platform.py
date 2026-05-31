from __future__ import annotations

from pydantic import BaseModel


class PlatformConfigRequest(BaseModel):
    config: dict[str, str]


class PlatformCallbackRequest(BaseModel):
    code: str
    state: str | None = None
    redirect_uri: str | None = None


class PlatformBindRequest(BaseModel):
    code: str
    state: str | None = None
    redirect_uri: str | None = None
