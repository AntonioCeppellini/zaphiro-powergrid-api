from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.components import Component
from app.models.measurements import Measurement


def create_measurement(db: Session, payload: dict) -> Measurement:
    component_id: UUID = payload["component_id"]

    component = db.execute(
        select(Component.id).where(Component.id == component_id)
    ).scalar_one_or_none()
    if component is None:
        raise LookupError("component_not_found")

    measurement = Measurement(**payload)
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement
