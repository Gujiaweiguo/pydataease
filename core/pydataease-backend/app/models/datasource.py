from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

type JSONValue = dict[str, object] | list[object]


@final
class CoreDatasource(Base):
    __tablename__ = "core_datasource"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    pid: Mapped[int | None] = mapped_column(ForeignKey("core_datasource.id"))
    edit_type: Mapped[str | None] = mapped_column(String(50))
    configuration: Mapped[JSONValue] = mapped_column(JSONB, nullable=False)
    create_time: Mapped[int] = mapped_column(BigInteger, nullable=False)
    update_time: Mapped[int] = mapped_column(BigInteger, nullable=False)
    update_by: Mapped[int | None] = mapped_column(BigInteger)
    create_by: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(Text)
    qrtz_instance: Mapped[str | None] = mapped_column(Text)
    task_status: Mapped[str | None] = mapped_column(String(50))
    enable_data_fill: Mapped[bool | None] = mapped_column(Boolean)


@final
class CoreDatasourceTask(Base):
    __tablename__ = "core_datasource_task"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    ds_id: Mapped[int] = mapped_column(ForeignKey("core_datasource.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    update_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[int | None] = mapped_column(BigInteger)
    sync_rate: Mapped[str] = mapped_column(String(50), nullable=False)
    cron: Mapped[str | None] = mapped_column(String(255))
    simple_cron_value: Mapped[int | None] = mapped_column(BigInteger)
    simple_cron_type: Mapped[str | None] = mapped_column(String(50))
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    last_exec_time: Mapped[int | None] = mapped_column(BigInteger)
    last_exec_status: Mapped[str | None] = mapped_column(String(50))
    extra_data: Mapped[JSONValue | None] = mapped_column(JSONB)
    task_status: Mapped[str | None] = mapped_column(String(50))


@final
class CoreDatasourceTaskLog(Base):
    __tablename__ = "core_datasource_task_log"
    __table_args__ = (  # pyright: ignore[reportAny]
        Index("idx_core_datasource_task_log_ds_id", "ds_id"),
        Index("idx_core_datasource_task_log_task_id", "task_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    ds_id: Mapped[int] = mapped_column(ForeignKey("core_datasource.id"), nullable=False)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("core_datasource_task.id"))
    start_time: Mapped[int | None] = mapped_column(BigInteger)
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    task_status: Mapped[str] = mapped_column(String(50), nullable=False)
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    info: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    trigger_type: Mapped[str | None] = mapped_column(String(45))
