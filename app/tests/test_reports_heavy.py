from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from app.models.components import Component, Transformer, Line, Switch
from app.models.measurements import Measurement
from app.models.reports import Report, ReportStatus
from app.report_worker import claim_one_report, process_report
from app.tests.auth import login


def test_reports_heavy_validation(client, db):
    """
    this test is done in order to validate quite everything i mean we have:
    - 100 components
    - 10000 measurements per component
    and we also generate differents reports for different periods
    """

    login(client)

    # cleaning the db so we can create controlled data
    db.execute(delete(Measurement))
    db.execute(delete(Report))
    db.execute(delete(Component))
    db.commit()

    # creating 100 components
    transformers = []
    lines = []
    switches = []

    # 34 transformers
    for i in range(1, 35):
        transformers.append(
            Transformer(
                component_type="transformer",
                name=f"T-{i}",
                substation="S1",
                capacity_mva=10.0,  # constant: makes expected total easy
                voltage_kv=132.0,
            )
        )

    # 33 lines
    for i in range(1, 34):
        lines.append(
            Line(
                component_type="line",
                name=f"L-{i}",
                substation="S2",
                length_km=1.0,  # constant: makes expected total easy
                voltage_kv=132.0,
            )
        )

    # 33 switches
    for i in range(1, 34):
        switches.append(
            Switch(
                component_type="switch",
                name=f"SW-{i}",
                substation="S3",
                status="closed",
            )
        )

    all_components = []
    all_components.extend(transformers)
    all_components.extend(lines)
    all_components.extend(switches)

    db.add_all(all_components)
    db.commit()

    assert len(all_components) >= 100

    # expected values (easy math)
    expected_count_transformers = len(transformers)
    expected_count_lines = len(lines)
    expected_count_switches = len(switches)

    # transformers with 10.0 MVA each at 132 kV
    expected_total_capacity_132 = float(expected_count_transformers) * 10.0

    # lines with 1.0 km each at 132 kV
    expected_total_length_132 = float(expected_count_lines) * 1.0

    # creating 10,000 measurements per component (1000000 total)
    now = datetime.now(timezone.utc)
    start_ts = now - timedelta(days=30)

    measurements_per_component = 10_000
    days_span = 30

    measurement_type_for_component = {
        "transformer": "Voltage",
        "line": "Current",
        "switch": "Power",
    }

    # inserting in chunk to not let my old pc explode
    batch_size = 50_000
    batch_rows = []

    for comp in all_components:
        mtype = measurement_type_for_component[comp.component_type]

        for i in range(measurements_per_component):
            # spreading timestamps across the 30-day period
            seconds_in_span = days_span * 24 * 3600
            offset_seconds = int((i / measurements_per_component) * seconds_in_span)
            ts = start_ts + timedelta(seconds=offset_seconds)

            # deterministic values so it's always valid
            value = float((i % 100) + 1)

            batch_rows.append(
                {
                    "component_id": comp.id,
                    "timestamp": ts,
                    "measurement_type": mtype,
                    "value": value,
                }
            )

            if len(batch_rows) >= batch_size:
                db.bulk_insert_mappings(Measurement, batch_rows)
                db.commit()
                batch_rows.clear()

    if batch_rows:
        db.bulk_insert_mappings(Measurement, batch_rows)
        db.commit()

    # function to create report and run worker in a single point to avoid repetitions
    def create_report_and_run_worker(from_date: datetime, to_date: datetime) -> Report:
        response = client.post(
            "/reports",
            json={
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat(),
            },
        )
        assert response.status_code == 202, response.text

        report_id = response.json()["id"]
        assert response.json()["status"] == ReportStatus.PENDING

        claimed = claim_one_report(db)
        assert claimed is not None
        assert str(claimed.id) == report_id
        assert claimed.status == ReportStatus.RUNNING

        report = db.get(Report, claimed.id)
        assert report is not None

        process_report(db, report)

        report = db.get(Report, claimed.id)
        assert report is not None
        assert report.status == ReportStatus.DONE

        return report

    # generating reports over different periods
    report_last_7_days = create_report_and_run_worker(now - timedelta(days=7), now)
    report_last_30_days = create_report_and_run_worker(now - timedelta(days=30), now)

    # validation
    reports = [report_last_7_days, report_last_30_days]

    for report in reports:
        # components by type
        components_by_type = report.components_by_type_json or []
        assert {"component_type": "transformer", "count": expected_count_transformers} in components_by_type
        assert {"component_type": "line", "count": expected_count_lines} in components_by_type
        assert {"component_type": "switch", "count": expected_count_switches} in components_by_type

        # transformer capacity per voltage
        transformer_capacity = report.transformer_capacity_by_voltage_json or []
        assert {"voltage_kv": 132.0, "capacity_mva": expected_total_capacity_132} in transformer_capacity

        # line length per voltage
        line_length = report.line_length_by_voltage_json or []
        assert {"voltage_kv": 132.0, "length_km": expected_total_length_132} in line_length

        # daily averages exist and contain the expected type pairs
        daily_averages = report.daily_measurement_averages_json or []
        assert len(daily_averages) > 0

        pairs = set()
        for row in daily_averages:
            pairs.add((row["component_type"], row["measurement_type"]))

        assert ("transformer", "Voltage") in pairs
        assert ("line", "Current") in pairs
        assert ("switch", "Power") in pairs
