from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Double, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

type JSONValue = dict[str, object] | list[object]


@final
class CoreExportTask(Base):
    __tablename__ = "core_export_task"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(2048))
    file_size: Mapped[float | None] = mapped_column(Double)
    file_size_unit: Mapped[str | None] = mapped_column(String(255))
    export_from: Mapped[int | None] = mapped_column(BigInteger)
    export_status: Mapped[str | None] = mapped_column(String(255))
    export_from_type: Mapped[str | None] = mapped_column(String(255))
    export_time: Mapped[int | None] = mapped_column(BigInteger)
    export_progress: Mapped[str | None] = mapped_column(String(255))
    export_machine_name: Mapped[str | None] = mapped_column(String(512))
    params: Mapped[JSONValue] = mapped_column(JSONB, nullable=False)
    msg: Mapped[str | None] = mapped_column(Text)
