from typing import TypeAlias

from pydantic import BaseModel


ResponseData: TypeAlias = object | list[object] | dict[str, object]


class ResultMessage(BaseModel):
    code: int = 200
    data: ResponseData | None = None
    msg: str = "success"
