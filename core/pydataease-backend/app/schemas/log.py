from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class LogGridRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    keyword: str | None = None
    op: str | None = None
    uid: int | None = None
    oid: int | None = None
    time: list[int] | None = None  # [start, end] epoch millis
    time_desc: bool = Field(
        default=True,
        validation_alias=AliasChoices("timeDesc", "time_desc"),
    )
    client: str | None = None


class LogGridVO(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    op_text: str | None = Field(None, serialization_alias="opText")
    op_detail: str | None = Field(None, serialization_alias="opDetail")
    name: str | None = None
    ip: str | None = None
    time: int | None = None
    success: bool | None = None
    msg: str | None = None


class LogOpVO(BaseModel):
    """Operation option tree node."""

    model_config = ConfigDict(populate_by_name=True)

    value: str
    label: str
    children: list["LogOpVO"] = []
