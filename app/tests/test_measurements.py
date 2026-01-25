# app/tests/test_measurements.py
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def test_create_measurement_happy(client):
    response = client.get("/components?limit=1&offset=0")
    assert response.status_code == 200, response.text
    component_id = response.json()[0]["id"]

    payload = {
        "component_id": component_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 123.45,
        "measurement_type": "Voltage",
    }

    response = client.post("/measurements", json=payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["component_id"] == component_id
    assert data["measurement_type"] == "Voltage"
    assert "id" in data


def test_create_measurement_component_not_found(client):
    payload = {
        "component_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 10.0,
        "measurement_type": "Current",
    }

    response = client.post("/measurements", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Component not found"


def test_create_measurement_invalid_payload(client):
    # missing measurement_type
    response = client.get("/components?limit=1&offset=0")
    component_id = response.json()[0]["id"]

    payload = {
        "component_id": component_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 10.0,
    }

    response = client.post("/measurements", json=payload)
    assert response.status_code == 422
