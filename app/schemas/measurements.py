from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MeasurementCreate(BaseModel):
    component_id: UUID
    timestamp: datetime
    value: float
    measurement_type: str = Field(min_length=1, max_length=50)


class MeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    component_id: UUID
    timestamp: datetime
    value: float
    measurement_type: str
