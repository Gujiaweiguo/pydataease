from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class TemplateTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str | None = None
    pid: str | None = None
    level: int | None = None
    dv_type: str | None = Field(None, serialization_alias="dvType")
    node_type: str | None = Field(None, serialization_alias="nodeType")
    create_time: int | None = Field(None, serialization_alias="createTime")
    snapshot: str | None = None
    template_type: str | None = Field(None, serialization_alias="templateType")
    children: list["TemplateTreeNode"] = []


class TemplateSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    pid: str | None = "0"
    dv_type: str | None = Field(
        "dashboard", validation_alias=AliasChoices("dvType", "dv_type")
    )
    node_type: str | None = Field(
        "panel", validation_alias=AliasChoices("nodeType", "node_type")
    )
    template_type: str | None = Field(
        "self", validation_alias=AliasChoices("templateType", "template_type")
    )
    snapshot: str | None = None
    template_style: dict | None = Field(
        None, validation_alias=AliasChoices("templateStyle", "template_style")
    )
    template_data: dict | None = Field(
        None, validation_alias=AliasChoices("templateData", "template_data")
    )
    dynamic_data: dict | None = Field(
        None, validation_alias=AliasChoices("dynamicData", "dynamic_data")
    )


class TemplateUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str | None = None
    snapshot: str | None = None
    template_style: dict | None = Field(
        None, validation_alias=AliasChoices("templateStyle", "template_style")
    )
    template_data: dict | None = Field(
        None, validation_alias=AliasChoices("templateData", "template_data")
    )
    dynamic_data: dict | None = Field(
        None, validation_alias=AliasChoices("dynamicData", "dynamic_data")
    )


class TemplateListRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    keyword: str | None = None


class CategoryFormRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category_id: str = Field(
        validation_alias=AliasChoices("categoryId", "category_id")
    )


class StoreToggleRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(
        validation_alias=AliasChoices("resourceId", "resource_id")
    )
    resource_type: int = Field(
        default=0, validation_alias=AliasChoices("resourceType", "resource_type")
    )
