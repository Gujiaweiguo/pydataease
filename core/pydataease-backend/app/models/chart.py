from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

type JSONValue = dict[str, object] | list[object]


@final
class CoreChartView(Base):
    __tablename__ = "core_chart_view"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    title: Mapped[str | None] = mapped_column(String(1024))
    scene_id: Mapped[int] = mapped_column(ForeignKey("data_visualization_info.id"), nullable=False)
    table_id: Mapped[int | None] = mapped_column(BigInteger)
    type: Mapped[str | None] = mapped_column(String(50))
    render: Mapped[str | None] = mapped_column(String(50))
    result_count: Mapped[int | None] = mapped_column(Integer)
    result_mode: Mapped[str | None] = mapped_column(String(50))
    x_axis: Mapped[JSONValue | None] = mapped_column(JSONB)
    x_axis_ext: Mapped[JSONValue | None] = mapped_column(JSONB)
    y_axis: Mapped[JSONValue | None] = mapped_column(JSONB)
    y_axis_ext: Mapped[JSONValue | None] = mapped_column(JSONB)
    ext_stack: Mapped[JSONValue | None] = mapped_column(JSONB)
    ext_bubble: Mapped[JSONValue | None] = mapped_column(JSONB)
    ext_label: Mapped[JSONValue | None] = mapped_column(JSONB)
    ext_tooltip: Mapped[JSONValue | None] = mapped_column(JSONB)
    custom_attr: Mapped[JSONValue | None] = mapped_column(JSONB)
    custom_style: Mapped[JSONValue | None] = mapped_column(JSONB)
    custom_filter: Mapped[JSONValue | None] = mapped_column(JSONB)
    drill_fields: Mapped[JSONValue | None] = mapped_column(JSONB)
    senior: Mapped[JSONValue | None] = mapped_column(JSONB)
    create_by: Mapped[str | None] = mapped_column(String(50))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    snapshot: Mapped[str | None] = mapped_column(Text)
    style_priority: Mapped[str | None] = mapped_column(String(255))
    chart_type: Mapped[str | None] = mapped_column(String(255))
    is_plugin: Mapped[bool | None] = mapped_column(Boolean)
    data_from: Mapped[str | None] = mapped_column(String(255))
    view_fields: Mapped[JSONValue | None] = mapped_column(JSONB)
    refresh_view_enable: Mapped[bool | None] = mapped_column(Boolean)
    refresh_unit: Mapped[str | None] = mapped_column(String(255))
    refresh_time: Mapped[int | None] = mapped_column(Integer)
    linkage_active: Mapped[bool | None] = mapped_column(Boolean)
    jump_active: Mapped[bool | None] = mapped_column(Boolean)
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)
    aggregate: Mapped[bool | None] = mapped_column(Boolean)
    flow_map_start_name: Mapped[JSONValue | None] = mapped_column(JSONB)
    flow_map_end_name: Mapped[JSONValue | None] = mapped_column(JSONB)
    ext_color: Mapped[JSONValue | None] = mapped_column(JSONB)
    custom_attr_mobile: Mapped[JSONValue | None] = mapped_column(JSONB)
    custom_style_mobile: Mapped[JSONValue | None] = mapped_column(JSONB)
    sort_priority: Mapped[JSONValue | None] = mapped_column(JSONB)
