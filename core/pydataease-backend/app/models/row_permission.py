from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreRowPermission(Base):
    __tablename__ = "core_row_permission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    dataset_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="FK to core_dataset_group.id")
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="org/role/user/sysvar")
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="org_id, role_id, user_id, or 0 for sysvar")
    filter_sql: Mapped[str] = mapped_column(Text, nullable=False, comment="WHERE clause fragment, e.g. region='east'")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    update_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
