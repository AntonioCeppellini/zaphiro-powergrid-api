from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_manager
from app.db.connection import get_db
from app.models.reports import Report, ReportStatus
from app.models.users import User
from app.schemas.reports import ReportCreate, ReportRead


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead, status_code=status.HTTP_202_ACCEPTED)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    if data.to_date <= data.from_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="to_date must be greater than from_date",
        )

    report = Report(
        from_date=data.from_date,
        to_date=data.to_date,
        status=ReportStatus.PENDING,
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=list[ReportRead])
def list_reports(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reports = select(Report).order_by(Report.created_at.desc()).offset(offset).limit(limit)
    return db.execute(reports).scalars().all()


@router.get("/{report_id}", response_model=ReportRead)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
