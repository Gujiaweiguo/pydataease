from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class OnlineMapSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str | None = None
    map_type: str | None = Field(
        default=None,
        validation_alias=AliasChoices("mapType", "map_type"),
        serialization_alias="mapType",
    )
    security_code: str | None = Field(
        default=None,
        validation_alias=AliasChoices("securityCode", "security_code"),
        serialization_alias="securityCode",
    )


class OnlineMapResponse(BaseModel):
    key: str | None = None
    map_type: str | None = Field(default=None, serialization_alias="mapType")
    security_code: str | None = Field(default=None, serialization_alias="securityCode")


class MenuResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    pid: int
    type: int | None = None
    name: str | None = None
    component: str | None = None
    menu_sort: int | None = Field(default=None, serialization_alias="menuSort")
    icon: str | None = None
    path: str | None = None
    hidden: bool = False
    in_layout: bool = Field(default=True, serialization_alias="inLayout")
    auth: bool = False


class MenuTreeNodeResponse(MenuResponse):
    children: list[MenuTreeNodeResponse] = Field(default_factory=list)
