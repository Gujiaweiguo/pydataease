from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

type JSONValue = dict[str, object] | list[object]


@final
class CoreDatasetGroup(Base):
    __tablename__ = "core_dataset_group"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str | None] = mapped_column(String(128))
    pid: Mapped[int | None] = mapped_column(ForeignKey("core_dataset_group.id"))
    level: Mapped[int | None] = mapped_column(Integer)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))
    mode: Mapped[int | None] = mapped_column(Integer)
    info: Mapped[JSONValue | None] = mapped_column(JSONB)
    create_by: Mapped[str | None] = mapped_column(String(50))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    qrtz_instance: Mapped[str | None] = mapped_column(String(1024))
    sync_status: Mapped[str | None] = mapped_column(String(45))
    update_by: Mapped[str | None] = mapped_column(String(50))
    last_update_time: Mapped[int | None] = mapped_column(BigInteger)
    union_sql: Mapped[str | None] = mapped_column(Text)
    is_cross: Mapped[bool | None] = mapped_column(Boolean)


@final
class CoreDatasetTable(Base):
    __tablename__ = "core_dataset_table"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str | None] = mapped_column(String(128))
    table_name: Mapped[str | None] = mapped_column(String(128))
    datasource_id: Mapped[int | None] = mapped_column(ForeignKey("core_datasource.id"))
    dataset_group_id: Mapped[int] = mapped_column(ForeignKey("core_dataset_group.id"), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))
    info: Mapped[str | None] = mapped_column(Text)
    sql_variable_details: Mapped[JSONValue | None] = mapped_column(JSONB)


@final
class CoreDatasetTableField(Base):
    __tablename__ = "core_dataset_table_field"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    datasource_id: Mapped[int | None] = mapped_column(ForeignKey("core_datasource.id"))
    dataset_table_id: Mapped[int | None] = mapped_column(ForeignKey("core_dataset_table.id"))
    dataset_group_id: Mapped[int | None] = mapped_column(ForeignKey("core_dataset_group.id"))
    chart_id: Mapped[int | None] = mapped_column(BigInteger)
    origin_name: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    dataease_name: Mapped[str | None] = mapped_column(String(255))
    field_short_name: Mapped[str | None] = mapped_column(String(255))
    group_list: Mapped[JSONValue | None] = mapped_column(JSONB)
    other_group: Mapped[JSONValue | None] = mapped_column(JSONB)
    group_type: Mapped[str | None] = mapped_column(String(50))
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int | None] = mapped_column(Integer)
    de_type: Mapped[int] = mapped_column(Integer, nullable=False)
    de_extract_type: Mapped[int] = mapped_column(Integer, nullable=False)
    ext_field: Mapped[int | None] = mapped_column(Integer)
    checked: Mapped[bool | None] = mapped_column(Boolean)
    column_index: Mapped[int | None] = mapped_column(Integer)
    last_sync_time: Mapped[int | None] = mapped_column(BigInteger)
    accuracy: Mapped[int | None] = mapped_column(Integer)
    date_format: Mapped[str | None] = mapped_column(String(255))
    date_format_type: Mapped[str | None] = mapped_column(String(255))
    params: Mapped[JSONValue | None] = mapped_column(JSONB)
    order_checked: Mapped[bool | None] = mapped_column(Boolean)
