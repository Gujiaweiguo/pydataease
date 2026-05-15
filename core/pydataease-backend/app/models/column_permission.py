from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreColumnPermission(Base):
    __tablename__ = "core_column_permission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    dataset_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="FK to core_dataset_group.id")
    field_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="FK to core_dataset_table_field.id")
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="org/role/user")
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="org_id, role_id, or user_id")
    action: Mapped[str] = mapped_column(String(20), nullable=False, comment="disable/desensitize/mask")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    update_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
