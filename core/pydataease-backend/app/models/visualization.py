from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

type JSONValue = dict[str, object] | list[object]


@final
class DataVisualizationInfo(Base):
    __tablename__ = "data_visualization_info"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str | None] = mapped_column(String(255))
    pid: Mapped[int | None] = mapped_column(ForeignKey("data_visualization_info.id"))
    org_id: Mapped[int | None] = mapped_column(BigInteger)
    level: Mapped[int | None] = mapped_column(Integer)
    node_type: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str | None] = mapped_column(String(50))
    canvas_style_data: Mapped[JSONValue | None] = mapped_column(JSONB)
    component_data: Mapped[JSONValue | None] = mapped_column(JSONB)
    mobile_layout: Mapped[bool | None] = mapped_column(Boolean)
    status: Mapped[int | None] = mapped_column(Integer)
    self_watermark_status: Mapped[int | None] = mapped_column(Integer)
    sort: Mapped[int | None] = mapped_column(Integer)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    create_by: Mapped[str | None] = mapped_column(String(255))
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    update_by: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str | None] = mapped_column(String(255))
    delete_flag: Mapped[bool | None] = mapped_column(Boolean)
    delete_time: Mapped[int | None] = mapped_column(BigInteger)
    delete_by: Mapped[str | None] = mapped_column(String(255))
    version: Mapped[int | None] = mapped_column(Integer)
    content_id: Mapped[str | None] = mapped_column(String(50))
    check_version: Mapped[str | None] = mapped_column(String(50))
