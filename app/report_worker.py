from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.connection import SessionLocal
from app.models.components import Component, Transformer, Line
from app.models.measurements import Measurement
from app.models.reports import Report, ReportStatus


logger = logging.getLogger("report-worker")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def claim_one_report(db: Session) -> Report | None:
    report = db.execute(
        select(Report)
        .where(Report.status == ReportStatus.PENDING)
        .order_by(Report.created_at.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    ).scalar_one_or_none()

    if report is None:
        return None

    report.status = ReportStatus.RUNNING
    report.job_started_at = _utcnow()
    report.error_message = None
    db.commit()

    return report


def compute_report(db: Session, report: Report):

    # components by type
    components_by_type = []
    res = db.execute(
        select(Component.component_type, func.count(Component.id)).group_by(
            Component.component_type
        )
    ).all()

    for component_type, count in res:
        components_by_type.append(
            {"component_type": component_type, "count": int(count)}
        )

    # transformer capacity per voltage
    transformer_capacity_by_voltage = []
    res = db.execute(
        select(
            Transformer.voltage_kv,
            func.coalesce(func.sum(Transformer.capacity_mva), 0.0),
        ).group_by(Transformer.voltage_kv)
    ).all()

    for voltage, capacity in res:
        transformer_capacity_by_voltage.append(
            {"voltage_kv": float(voltage), "capacity_mva": float(capacity)}
        )

    # line length per voltage
    line_length_by_voltage = []
    res = db.execute(
        select(
            Line.voltage_kv,
            func.coalesce(func.sum(Line.length_km), 0.0),
        ).group_by(Line.voltage_kv)
    ).all()

    for voltage, length in res:
        line_length_by_voltage.append(
            {"voltage_kv": float(voltage), "length_km": float(length)}
        )

    # daily measurement averages
    daily_measurement_averages = []

    day_bucket = func.date_trunc("day", Measurement.timestamp).label("day")

    res = db.execute(
        select(
            day_bucket,
            Measurement.measurement_type,
            Component.component_type,
            func.avg(Measurement.value),
        )
        .join(Component, Component.id == Measurement.component_id)
        .where(Measurement.timestamp >= report.from_date)
        .where(Measurement.timestamp < report.to_date)
        .group_by(day_bucket, Measurement.measurement_type, Component.component_type)
        .order_by(day_bucket.asc())
    ).all()

    for day, measurement_type, component_type, avg_value in res:
        daily_measurement_averages.append(
            {
                "day": day.date().isoformat(),
                "measurement_type": measurement_type,
                "component_type": component_type,
                "avg_value": float(avg_value) if avg_value else None,
            }
        )

    return (
        components_by_type,
        transformer_capacity_by_voltage,
        line_length_by_voltage,
        daily_measurement_averages,
    )


def process_report(db: Session, report: Report) -> None:
    try:
        (
            components_by_type,
            transformer_capacity_by_voltage,
            line_length_by_voltage,
            daily_measurement_averages,
        ) = compute_report(db, report)

        report.components_by_type_json = components_by_type
        report.transformer_capacity_by_voltage_json = transformer_capacity_by_voltage
        report.line_length_by_voltage_json = line_length_by_voltage
        report.daily_measurement_averages_json = daily_measurement_averages

        report.status = ReportStatus.DONE
        report.job_finished_at = _utcnow()
        db.commit()

    except Exception as exc:
        db.rollback()
        report = db.get(Report, report.id)

        report.attempts += 1
        report.job_finished_at = _utcnow()
        report.error_message = str(exc)

        if report.attempts >= settings.REPORT_MAX_ATTEMPTS:
            report.status = ReportStatus.FAILED
        else:
            report.status = ReportStatus.PENDING

        db.commit()


def run_once(db) -> bool:
    report = claim_one_report(db)
    if not report:
        return False

    report = db.get(Report, report.id)
    if not report:
        return False
    process_report(db, report)
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    while True:
        with SessionLocal() as db:
            did_work = run_once(db)
        if not did_work:
            time.sleep(2)


if __name__ == "__main__":
    main()
