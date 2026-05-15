from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrgTreeRequest(BaseModel):
    keyword: str | None = None


class OrgMountedRequest(BaseModel):
    keyword: str | None = None


class OrgCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    pid: int | None = 0


class OrgEditRequest(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=255)


class OrgResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pid: int | None = None
    name: str
    create_time: int | None = None
    update_time: int | None = None


class OrgTreeNode(BaseModel):
    id: str
    pid: str | int
    name: str
    leaf: bool
    weight: int = 9
    extraFlag: int = 0
    extraFlag1: int = 0
    children: list[OrgTreeNode] = Field(default_factory=list)


class OrgResourceExistResponse(BaseModel):
    exists: bool
