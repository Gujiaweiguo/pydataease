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


class RoleBeforeUnmountRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_id: int = Field(validation_alias=AliasChoices("roleId", "role_id"), serialization_alias="roleId")
    user_ids: list[int] = Field(
        default_factory=list,
        validation_alias=AliasChoices("userIds", "user_ids"),
        serialization_alias="userIds",
    )


class RoleBeforeUnmountInfoItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str | None = None
    account: str | None = None
    remaining_role_count: int = Field(default=0, serialization_alias="remainingRoleCount")


class RoleBeforeUnmountInfoResponse(BaseModel):
    items: list[RoleBeforeUnmountInfoItem] = Field(default_factory=list)


class RoleMountExternalRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_id: int = Field(validation_alias=AliasChoices("roleId", "role_id"), serialization_alias="roleId")
    accounts: list[str] = Field(default_factory=list)


class RoleMountExternalResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mounted: list[str] = Field(default_factory=list)
    not_found: list[str] = Field(default_factory=list, serialization_alias="notFound")


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


class RoleCreateWithPermsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    permission_point_names: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("permissionPointNames", "permission_point_names"),
        serialization_alias="permissionPointNames",
    )
    user_ids: list[int] = Field(
        default_factory=list,
        validation_alias=AliasChoices("userIds", "user_ids"),
        serialization_alias="userIds",
    )


class RoleSetPermsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    permission_point_names: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("permissionPointNames", "permission_point_names"),
        serialization_alias="permissionPointNames",
    )


class PermissionPointVO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str | None = None
    permission_type: str = Field(serialization_alias="permissionType")
    granted: bool = True


class RolePermissionDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_id: int = Field(serialization_alias="roleId")
    role_name: str = Field(serialization_alias="roleName")
    permissions: list[PermissionPointVO] = Field(default_factory=list)
