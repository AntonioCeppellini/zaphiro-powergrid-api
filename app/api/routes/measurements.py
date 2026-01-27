from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.schemas.measurements import MeasurementCreate, MeasurementRead
from app.services.measurements import create_measurement

from app.api.deps import require_manager
from app.models.users import User

router = APIRouter(prefix="/measurements", tags=["measurement"])


@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def measurements_create(
    data: MeasurementCreate, db: Session = Depends(get_db), user=Depends(require_manager)
):
    try:
        return create_measurement(db, payload=data.model_dump())
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Component not found"
        )
