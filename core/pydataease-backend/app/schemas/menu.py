from __future__ import annotations

from pydantic import BaseModel


class MenuMeta(BaseModel):
    title: str
    icon: str | None = None


class MenuVO(BaseModel):
    path: str
    component: str | None = None
    hidden: bool = False
    isPlugin: bool = False
    name: str
    inLayout: bool = True
    redirect: str | None = None
    meta: MenuMeta
    children: list["MenuVO"] = []
