from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    name: str
    pwd: str
    origin: int = 0


class TokenResponse(BaseModel):
    token: str
    exp: int
