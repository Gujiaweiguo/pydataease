from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class CoreMenu(Base):
    __tablename__ = "core_menu"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    pid: Mapped[int] = mapped_column(ForeignKey("core_menu.id"), nullable=False)
    type: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String(45))
    component: Mapped[str | None] = mapped_column(String(45))
    menu_sort: Mapped[int | None] = mapped_column(Integer)
    icon: Mapped[str | None] = mapped_column(String(45))
    path: Mapped[str | None] = mapped_column(String(45))
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    in_layout: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auth: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
