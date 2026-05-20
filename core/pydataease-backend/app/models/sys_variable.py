from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class CoreSysVariable(Base):
    __tablename__ = "core_sys_variable"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    alias: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset_group_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    dataset_table_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    update_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    create_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@final
class CoreSysVariableValue(Base):
    __tablename__ = "core_sys_variable_value"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    variable_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    update_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
