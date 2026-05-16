from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class DatasetTableSqlLog(Base):
    __tablename__ = "core_dataset_table_sql_log"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    table_id: Mapped[str | None] = mapped_column(String(50))
    sql_snapshot: Mapped[str | None] = mapped_column(Text)
    table_name: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    create_by: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str | None] = mapped_column(String(255))
    error_msg: Mapped[str | None] = mapped_column(Text)
