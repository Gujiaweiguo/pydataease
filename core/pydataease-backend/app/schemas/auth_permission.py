from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class BusiPermissionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(validation_alias=AliasChoices("id", "id"))
    type: int = Field(validation_alias=AliasChoices("type", "type"), description="0=user, 1=role, 2=org")
    flag: str = Field(
        validation_alias=AliasChoices("flag", "flag"),
        description="dashboard/screen/dataset/datasource",
    )


class MenuPermissionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(validation_alias=AliasChoices("id", "id"))


class PermissionItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | str
    weight: int = 0
    column_permissions: object | None = Field(
        default=None,
        validation_alias=AliasChoices("columnPermissions", "column_permissions"),
        serialization_alias="columnPermissions",
    )
    row_permissions: object | None = Field(
        default=None,
        validation_alias=AliasChoices("rowPermissions", "row_permissions"),
        serialization_alias="rowPermissions",
    )
    ext: int = 0


class BusiPerEditor(BusiPermissionRequest):
    permissions: list[PermissionItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("permissions", "permissions"),
    )


class MenuPerEditor(MenuPermissionRequest):
    permissions: list[PermissionItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("permissions", "permissions"),
    )


class TargetPerCreator(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ids: list[int] = Field(default_factory=list, validation_alias=AliasChoices("ids", "ids"))


class MenuTargetPerCreator(TargetPerCreator):
    permissions: list[PermissionItem] = Field(
        default_factory=list,
        validation_alias=AliasChoices("permissions", "permissions"),
    )


class BusiTargetPerCreator(MenuTargetPerCreator):
    type: int = Field(default=0, validation_alias=AliasChoices("type", "type"))
    flag: str = Field(default="", validation_alias=AliasChoices("flag", "flag"))


class ResourceVO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | int
    name: str
    children: list[ResourceVO] = Field(default_factory=list, serialization_alias="children")
    leaf: bool = False
    extra_flag: int = Field(
        default=0,
        validation_alias=AliasChoices("extraFlag", "extra_flag"),
        serialization_alias="extraFlag",
    )


class PermissionOrigin(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | str
    name: str
    permissions: list[PermissionItem] = Field(default_factory=list)


class PermissionVO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    root: bool = False
    readonly: bool = False
    permissions: list[PermissionItem] = Field(default_factory=list)
    permission_origins: list[PermissionOrigin] = Field(
        default_factory=list,
        validation_alias=AliasChoices("permissionOrigins", "permission_origins"),
        serialization_alias="permissionOrigins",
    )


class UserOrgOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account: str
    name: str
    email: str | None = None


ResourceVO.model_rebuild()
