from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    component_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    value: Mapped[float] = mapped_column(Float, nullable=False)

    measurement_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )

    component: Mapped["Component"] = relationship(
        "Component", back_populates="measurements"
    )

    __table_args__ = (
        Index("ix_measurements_component_type_time", "component_id", "measurement_type", "timestamp"),
    )
