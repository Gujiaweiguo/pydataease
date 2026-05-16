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
    access_count: int = 0


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


class TicketValidVO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ticket_valid: bool = Field(default=True, serialization_alias="ticketValid")
    ticket_exp: bool = Field(default=False, serialization_alias="ticketExp")
    args: str = ""


class ProxyInfoResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: str = Field(serialization_alias="resourceId")
    uid: str
    exp: bool
    pwd_valid: bool = Field(serialization_alias="pwdValid")
    type: str
    in_iframe_error: bool = Field(default=False, serialization_alias="inIframeError")
    share_disable: bool = Field(default=False, serialization_alias="shareDisable")
    pe_require_valid: bool = Field(default=True, serialization_alias="peRequireValid")
    ticket_valid_vo: TicketValidVO = Field(serialization_alias="ticketValidVO")
    uuid: str


class ShareEditExpRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(validation_alias=AliasChoices("resourceId", "resource_id"))
    exp: int = 0


class ShareEditPwdRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(validation_alias=AliasChoices("resourceId", "resource_id"))
    pwd: str = ""
    auto_pwd: bool = Field(default=True, validation_alias=AliasChoices("autoPwd", "auto_pwd"))


class ShareEditUuidRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(validation_alias=AliasChoices("resourceId", "resource_id"))
    uuid: str


class ShareQueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str | None = None
    keyword: str | None = None
    query_from: str | None = Field(
        default=None, validation_alias=AliasChoices("queryFrom", "query_from")
    )
    asc: bool = False


class TicketSwitchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: str = Field(validation_alias=AliasChoices("resourceId", "resource_id"))
    require: bool = False


class ShareTicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    uuid: str
    ticket: str
    exp: int | None = None
    args: JSONDict | JSONList | None = None
    access_time: int | None = Field(default=None, serialization_alias="accessTime")
