from __future__ import annotations

from datetime import datetime, timezone

from app.models.components import Component, Transformer, Line, Switch
from app.models.measurements import Measurement
from app.models.reports import Report, ReportStatus

from app.tests.auth import login, logout

from app.report_worker import claim_one_report, process_report

from sqlalchemy import select, delete


def test_worker_expected_vs_actual_all_aggregations(client, db):
    """
    a bit complicated test sooooo:
    - cleaning DB tables
    - create known components and measurements (to do easy maths)
    - manually do the maths
    - run worker
    - compare expected against actual
    """

    login(client)

    # cleaning like cinderella
    db.execute(delete(Measurement))
    db.execute(delete(Report))
    db.execute(delete(Component))
    db.commit()

    # creating components
    transformers = []
    lines = []
    switches = []

    for i in range(1, 5):
        transformers.append(
            Transformer(
                component_type="transformer",
                name=f"T-{i}",
                substation="S1",
                capacity_mva=float(i * 10),  # 10,20,30,40
                voltage_kv=132.0,
            )
        )

    for i in range(1, 5):
        lines.append(
            Line(
                component_type="line",
                name=f"L-{i}",
                substation="S2",
                length_km=float(i),  # 1,2,3,4
                voltage_kv=132.0,
            )
        )

    for i in range(1, 5):
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

    # creating measurements with the same timestamp
    # so they fall in the same daily bucket
    ts = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)

    measurements = []

    # voltage: 10,20,30,40 so avg 25
    # using enumerate to not use the C style i++
    for i, t in enumerate(transformers, start=1):
        measurements.append(
            Measurement(
                component_id=t.id,
                timestamp=ts,
                measurement_type="Voltage",
                value=float(i * 10),
            )
        )

    # current: 1,2,3,4 so avg 2.5
    for i, l in enumerate(lines, start=1):
        measurements.append(
            Measurement(
                component_id=l.id,
                timestamp=ts,
                measurement_type="Current",
                value=float(i),
            )
        )

    # power: 100,200,300,400 so avg 250
    for i, s in enumerate(switches, start=1):
        measurements.append(
            Measurement(
                component_id=s.id,
                timestamp=ts,
                measurement_type="Power",
                value=float(i * 100),
            )
        )

    db.add_all(measurements)
    db.commit()

    # creating report
    from_date = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    to_date = datetime(2026, 1, 11, 0, 0, tzinfo=timezone.utc)

    response = client.post(
        "/reports",
        json={
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
        },
    )

    assert response.status_code == 202
    assert response.json()["status"] == ReportStatus.PENDING
    report_id = response.json()["id"]

    # launching the worker
    claimed = claim_one_report(db)
    assert claimed is not None
    assert str(claimed.id) == report_id
    assert claimed.status == ReportStatus.RUNNING

    report = db.get(Report, claimed.id)
    process_report(db, report)

    report = db.get(Report, claimed.id)
    assert report.status == ReportStatus.DONE

    # building expected things
    expected_components_by_type = [
        {"component_type": "transformer", "count": 4},
        {"component_type": "line", "count": 4},
        {"component_type": "switch", "count": 4},
    ]

    expected_transformer_capacity_by_voltage = [
        {"voltage_kv": 132.0, "capacity_mva": 100.0},
    ]

    expected_line_length_by_voltage = [
        {"voltage_kv": 132.0, "length_km": 10.0},
    ]

    expected_daily_averages = [
        {
            "day": "2026-01-10",
            "measurement_type": "Voltage",
            "component_type": "transformer",
            "avg_value": 25.0,
        },
        {
            "day": "2026-01-10",
            "measurement_type": "Current",
            "component_type": "line",
            "avg_value": 2.5,
        },
        {
            "day": "2026-01-10",
            "measurement_type": "Power",
            "component_type": "switch",
            "avg_value": 250.0,
        },
    ]

    # taking the actual things from db (hopefully they are equal to the expected ones :D)
    # NARRATOR: "they were not equal"
    actual_components_by_type = report.components_by_type_json
    actual_transformer_capacity_by_voltage = report.transformer_capacity_by_voltage_json
    actual_line_length_by_voltage = report.line_length_by_voltage_json
    actual_daily_averages = report.daily_measurement_averages_json

    # ACTUAL
    # VS
    # EXPECTED
    assert len(actual_components_by_type) == len(expected_components_by_type)
    for item in expected_components_by_type:
        assert item in actual_components_by_type

    assert len(actual_transformer_capacity_by_voltage) == len(
        expected_transformer_capacity_by_voltage
    )
    for item in expected_transformer_capacity_by_voltage:
        assert item in actual_transformer_capacity_by_voltage

    assert len(actual_line_length_by_voltage) == len(expected_line_length_by_voltage)
    for item in expected_line_length_by_voltage:
        assert item in actual_line_length_by_voltage

    assert len(actual_daily_averages) == len(expected_daily_averages)
    for expected in expected_daily_averages:
        found = False
        for actual in actual_daily_averages:
            if (
                actual["day"] == expected["day"]
                and actual["measurement_type"] == expected["measurement_type"]
                and actual["component_type"] == expected["component_type"]
            ):
                assert abs(actual["avg_value"] - expected["avg_value"]) < 1e-9
                found = True
        assert found, f"Missing daily average row: {expected}"
