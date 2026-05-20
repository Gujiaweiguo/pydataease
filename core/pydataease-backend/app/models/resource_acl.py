from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreResourceAcl(Base):
    __tablename__ = "core_resource_acl"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="role/user/org")
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="Role ID, User ID, or Org ID")
    resource_type: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment="dashboard/screen/dataset/datasource",
    )
    resource_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Specific resource (visualization/dataset/datasource) ID",
    )
    weight: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Permission weight: 1=read, 2=use, 4=export, 7=manage, 9=authorize",
    )
    ext: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="Extended permission weight")
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    update_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
