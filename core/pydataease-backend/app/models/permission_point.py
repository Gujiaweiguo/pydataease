from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CorePermissionPoint(Base):
    __tablename__ = "core_permission_point"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    menu_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="FK to core_menu.id, NULL for resource-type points")
    resource_type: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="dashboard/screen/dataset/datasource")
    permission_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="use/manage/authorize/view/export")
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="Human-readable name")
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
