from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class UserPagerRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    keyword: str | None = None
    enable: bool | None = None


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    account: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=255)
    role_ids: list[int] | None = Field(
        default=None,
        validation_alias=AliasChoices("roleIds", "role_ids"),
        serialization_alias="roleIds",
    )
    oid: int | None = None


class UserEditRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=255)
    role_ids: list[int] | None = Field(
        default=None,
        validation_alias=AliasChoices("roleIds", "role_ids"),
        serialization_alias="roleIds",
    )


class UserEnableRequest(BaseModel):
    id: int
    enable: bool


class UserRoleSelectedRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_id: int = Field(validation_alias=AliasChoices("roleId", "role_id"), serialization_alias="roleId")


class UserByCurrentOrgRequest(BaseModel):
    keyword: str | None = None


class UserOrgMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    pid: int | None = None


class UserRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    oid: int
    type: int


class UserListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    account: str
    name: str
    email: str | None = None
    phone: str | None = None
    enable: bool
    oid: int | None = None
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    update_time: int | None = Field(default=None, serialization_alias="updateTime")
    role_ids: list[int] = Field(default_factory=list, serialization_alias="roleIds")
    org_ids: list[int] = Field(default_factory=list, serialization_alias="orgIds")


class UserPagerResponse(BaseModel):
    items: list[UserListItemResponse]
    total: int


class UserDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    account: str
    name: str
    email: str | None = None
    phone: str | None = None
    enable: bool
    oid: int | None = None
    role_ids: list[int] = Field(default_factory=list, serialization_alias="roleIds")
    roles: list[UserRoleResponse] = Field(default_factory=list)
    org_ids: list[int] = Field(default_factory=list, serialization_alias="orgIds")
    orgs: list[UserOrgMembershipResponse] = Field(default_factory=list)
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    update_time: int | None = Field(default=None, serialization_alias="updateTime")


class DefaultPasswordResponse(BaseModel):
    password: str
