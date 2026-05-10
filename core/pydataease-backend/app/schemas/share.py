from __future__ import annotations

from typing import TypeAlias

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

JSONDict: TypeAlias = dict[str, object]
JSONList: TypeAlias = list[object]


class ShareCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(validation_alias=AliasChoices("resourceId", "resource_id"))
    type: int = 0
    oid: int = 0
    auto_pwd: bool | None = Field(
        default=True,
        validation_alias=AliasChoices("autoPwd", "auto_pwd"),
    )
    exp: int | None = None
    pwd: str | None = None
    uuid: str | None = None


class ShareProxyInfoRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid: str
    ciphertext: str | None = None
    in_iframe: bool | None = Field(
        default=False,
        validation_alias=AliasChoices("inIframe", "in_iframe"),
    )
    ticket: str | None = None


class ShareDetailRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(validation_alias=AliasChoices("resourceId", "resource_id"))


class ShareDeleteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(validation_alias=AliasChoices("resourceId", "resource_id"))


class ShareViewDetailRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid: str


class ShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    creator: int
    time: int
    exp: int | None = None
    uuid: str
    pwd: str | None = None
    resource_id: int = Field(serialization_alias="resourceId")
    oid: int
    type: int
    auto_pwd: bool | None = Field(default=None, serialization_alias="autoPwd")
    ticket_require: bool | None = Field(default=None, serialization_alias="ticketRequire")


class ShareTicketSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid: str | None = None
    ticket: str
    exp: int | None = None
    args: JSONDict | JSONList | None = None
    generate_new: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("generateNew", "generate_new"),
    )


class ShareTicketDeleteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ticket: str


class ShareTicketDetailRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid: str


class ShareTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    uuid: str
    ticket: str
    exp: int | None = None
    args: JSONDict | JSONList | None = None
    access_time: int | None = Field(default=None, serialization_alias="accessTime")
