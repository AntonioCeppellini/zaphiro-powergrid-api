from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    from_date: datetime
    to_date: datetime


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    from_date: datetime
    to_date: datetime

    status: str

    created_at: datetime
    job_started_at: datetime | None = None
    job_finished_at: datetime | None = None

    attempts: int

    error_message: str | None = None

    components_by_type_json: list[dict] | None = None
    transformer_capacity_by_voltage_json: list[dict] | None = None
    line_length_by_voltage_json: list[dict] | None = None
    daily_measurement_averages_json: list[dict] | None = None

