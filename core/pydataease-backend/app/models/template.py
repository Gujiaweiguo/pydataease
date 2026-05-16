from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class VisualizationTemplate(Base):
    __tablename__ = "visualization_template"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    pid: Mapped[str | None] = mapped_column(String(255))
    level: Mapped[int | None] = mapped_column(Integer)
    dv_type: Mapped[str | None] = mapped_column(String(255))
    node_type: Mapped[str | None] = mapped_column(String(255))
    create_by: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    snapshot: Mapped[str | None] = mapped_column(Text)
    template_type: Mapped[str | None] = mapped_column(String(255))
    template_style: Mapped[dict | None] = mapped_column(JSONB)
    template_data: Mapped[dict | None] = mapped_column(JSONB)
    dynamic_data: Mapped[dict | None] = mapped_column(JSONB)


@final
class VisualizationTemplateCategory(Base):
    __tablename__ = "visualization_template_category"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    pid: Mapped[str | None] = mapped_column(String(255))
    level: Mapped[int | None] = mapped_column(Integer)
    dv_type: Mapped[str | None] = mapped_column(String(255))
    node_type: Mapped[str | None] = mapped_column(String(255))
    create_by: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    snapshot: Mapped[str | None] = mapped_column(Text)
    template_type: Mapped[str | None] = mapped_column(String(255))


@final
class VisualizationTemplateCategoryMap(Base):
    __tablename__ = "visualization_template_category_map"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    category_id: Mapped[str | None] = mapped_column(String(255))
    template_id: Mapped[str | None] = mapped_column(String(255))
