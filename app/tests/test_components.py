from __future__ import annotations

import uuid


# get
def test_list_components_happy(client):
    response = client.get("/components")
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 9  # seed: 3 transformer, 3 line, 3 switch


def test_list_components_filter_by_type(client):
    response = client.get("/components?component_type=transformer")
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 3
    assert all(component["component_type"] == "transformer" for component in data)


def test_list_components_filter_by_substation(client):
    response = client.get("/components?substation=S2")
    assert response.status_code == 200, response.text

    data = response.json()
    assert len(data) == 3
    assert all(component["substation"] == "S2" for component in data)


# post
def test_create_component_happy(client):
    payload = {
        "component_type": "transformer",
        "name": "T-new",
        "substation": "S9",
        "capacity_mva": 200.0,
        "voltage_kv": 220.0,
    }

    response = client.post("/components", json=payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["name"] == "T-new"
    assert data["component_type"] == "transformer"
    assert "id" in data


def test_create_component_invalid_payload(client):
    # missing capacity_mva
    payload = {
        "component_type": "transformer",
        "name": "BROKEN",
        "substation": "S1",
        "voltage_kv": 132.0,
    }

    response = client.post("/components", json=payload)
    assert response.status_code == 422


# helper
def _create_transformer(client):
    payload = {
        "component_type": "transformer",
        "name": "T-upd",
        "substation": "S1",
        "capacity_mva": 100.0,
        "voltage_kv": 132.0,
    }
    response = client.post("/components", json=payload)
    assert response.status_code == 200
    return response.json()


def test_update_component_happy(client):
    component = _create_transformer(client)

    update_payload = {
        "component_type": "transformer",
        "name": "T-updated",
        "substation": "S99",
        "capacity_mva": 150.0,
        "voltage_kv": 220.0,
    }

    response = client.put(f"/components/{component['id']}", json=update_payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["name"] == "T-updated"
    assert data["capacity_mva"] == 150.0
    assert data["voltage_kv"] == 220.0


def test_update_component_not_found(client):
    fake_id = str(uuid.uuid4())

    payload = {
        "component_type": "transformer",
        "name": "X",
        "substation": "S1",
        "capacity_mva": 1.0,
        "voltage_kv": 1.0,
    }

    response = client.put(f"/components/{fake_id}", json=payload)
    assert response.status_code == 404


def test_update_component_type_mismatch(client):
    component = _create_transformer(client)

    # changing type
    payload = {
        "component_type": "line",
        "name": "L-hacker",
        "substation": "S1",
        "length_km": 10.0,
        "voltage_kv": 132.0,
    }

    response = client.put(f"/components/{component['id']}", json=payload)
    assert response.status_code == 409


def test_update_component_missing_type(client):
    component = _create_transformer(client)

    payload = {
        "name": "NO-TYPE",
        "substation": "S1",
        "capacity_mva": 99.0,
        "voltage_kv": 132.0,
    }

    response = client.put(f"/components/{component['id']}", json=payload)
    assert response.status_code == 422 or r.status_code == 400


# delete
def test_delete_component_happy(client):
    component = _create_transformer(client)

    response = client.delete(f"/components/{component['id']}")
    assert response.status_code == 204

    # veryfing it is deleted
    response = client.get("/components?component_type=transformer")
    ids = [x["id"] for x in response.json()]
    assert component["id"] not in ids


def test_delete_component_not_found(client):
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/components/{fake_id}")
    assert response.status_code == 404
