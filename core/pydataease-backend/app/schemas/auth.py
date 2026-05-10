from pydantic import BaseModel


class TokenUser(BaseModel):
    user_id: int
    oid: int
    language: str = "zh-CN"
