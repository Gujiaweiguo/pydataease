from __future__ import annotations

from typing import final

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class MapGeo(Base):
    __tablename__ = "map_geo"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    geo_json: Mapped[dict | None] = mapped_column(JSONB)
