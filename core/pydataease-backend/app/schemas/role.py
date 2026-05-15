from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class RoleQueryRequest(BaseModel):
    keyword: str | None = None


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class RoleEditRequest(BaseModel):
    id: int
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class RoleUserOptionRequest(BaseModel):
    keyword: str | None = None


class RoleMountRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_id: int = Field(validation_alias=AliasChoices("roleId", "role_id"), serialization_alias="roleId")
    user_ids: list[int] = Field(
        validation_alias=AliasChoices("userIds", "user_ids"),
        serialization_alias="userIds",
    )


class RoleUnmountRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_id: int = Field(validation_alias=AliasChoices("roleId", "role_id"), serialization_alias="roleId")
    user_ids: list[int] = Field(
        validation_alias=AliasChoices("userIds", "user_ids"),
        serialization_alias="userIds",
    )


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    oid: int
    type: int
    create_time: int | None = None
    update_time: int | None = None


class RoleDetailResponse(RoleResponse):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    member_count: int = Field(serialization_alias="memberCount")


class RoleUserOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account: str
    name: str
    email: str | None = None
    phone: str | None = None
    enable: bool
