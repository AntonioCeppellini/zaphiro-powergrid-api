from __future__ import annotations
import uuid
import enum

from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Float,
    Enum,
    Index,
    DateTime,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base


class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"),
        nullable=False,
        index=True,
        default=ReportStatus.PENDING,
    )

    from_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    to_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    job_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    job_finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    error_message: Mapped[str | None] = mapped_column(Text)

    components_by_type_json: Mapped[list[dict] | None] = mapped_column(JSONB)
    transformer_capacity_by_voltage_json: Mapped[list[dict] | None] = mapped_column(
        JSONB
    )
    line_length_by_voltage_json: Mapped[list[dict] | None] = mapped_column(JSONB)
    daily_measurement_averages_json: Mapped[list[dict] | None] = mapped_column(JSONB)
