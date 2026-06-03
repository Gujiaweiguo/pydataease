from __future__ import annotations

import json

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


JsonObject = dict[str, object]
JsonArray = list[object]


def _parse_json_value(value: object) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        return json.loads(stripped)
    return value


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
    categories: list[str] | None = None
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
    template_style: JsonObject | None = Field(
        None, validation_alias=AliasChoices("templateStyle", "template_style")
    )
    template_data: JsonObject | JsonArray | None = Field(
        None, validation_alias=AliasChoices("templateData", "template_data")
    )
    dynamic_data: JsonObject | JsonArray | None = Field(
        None, validation_alias=AliasChoices("dynamicData", "dynamic_data")
    )

    @field_validator("template_style", "template_data", "dynamic_data", mode="before")
    @classmethod
    def parse_serialized_json(cls, value: object) -> object:
        return _parse_json_value(value)


class TemplateUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str | None = None
    snapshot: str | None = None
    template_style: JsonObject | None = Field(
        None, validation_alias=AliasChoices("templateStyle", "template_style")
    )
    template_data: JsonObject | JsonArray | None = Field(
        None, validation_alias=AliasChoices("templateData", "template_data")
    )
    dynamic_data: JsonObject | JsonArray | None = Field(
        None, validation_alias=AliasChoices("dynamicData", "dynamic_data")
    )

    @field_validator("template_style", "template_data", "dynamic_data", mode="before")
    @classmethod
    def parse_serialized_json(cls, value: object) -> object:
        return _parse_json_value(value)


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


class TemplateFindRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    template_id: str | None = Field(
        None, validation_alias=AliasChoices("templateId", "template_id")
    )


class FindCategoriesRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dv_type: str | None = Field(
        None, validation_alias=AliasChoices("dvType", "dv_type")
    )
    template_type: str | None = Field(
        None, validation_alias=AliasChoices("templateType", "template_type")
    )


class NameCheckRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    id: str | None = None
    opt_type: str | None = Field(
        None, validation_alias=AliasChoices("optType", "opt_type")
    )


class CategoryTemplateNameCheckRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    categories: list[str] | None = None


class BatchDeleteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    template_ids: list[str] | None = Field(
        None, validation_alias=AliasChoices("templateIds", "template_ids")
    )
    categories: list[str] | None = None


class BatchUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    template_ids: list[str] | None = Field(
        None, validation_alias=AliasChoices("templateIds", "template_ids")
    )
    categories: list[str] | None = None


class FindCategoriesByTemplateIdsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    template_ids: list[str] = Field(
        validation_alias=AliasChoices("templateIds", "template_ids")
    )


class TemplateListBodyRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category_id: str | None = Field(
        None, validation_alias=AliasChoices("categoryId", "category_id")
    )
    dv_type: str | None = Field(
        None, validation_alias=AliasChoices("dvType", "dv_type")
    )
    template_type: str | None = Field(
        None, validation_alias=AliasChoices("templateType", "template_type")
    )
    keyword: str | None = None
