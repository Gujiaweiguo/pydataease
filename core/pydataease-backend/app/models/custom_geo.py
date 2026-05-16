from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class CustomGeoArea(Base):
    __tablename__ = "custom_geo_area"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    create_by: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    update_by: Mapped[str | None] = mapped_column(String(255))
    update_time: Mapped[int | None] = mapped_column(BigInteger)


@final
class CustomGeoSubArea(Base):
    __tablename__ = "custom_geo_sub_area"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    geo_area_id: Mapped[str | None] = mapped_column(String(50))
    name: Mapped[str | None] = mapped_column(String(255))
    geo_json: Mapped[dict | None] = mapped_column(JSONB)
