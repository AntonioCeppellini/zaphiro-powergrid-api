from __future__ import annotations

import uuid

from app.tests.auth import login, logout


COMPONENT = {
    "component_type": "transformer",
    "name": "T-new",
    "substation": "S9",
    "capacity_mva": 200.0,
    "voltage_kv": 220.0,
}

UPDATE_COMPONENT = {
    "component_type": "transformer",
    "name": "T-updated",
    "substation": "S99",
    "capacity_mva": 150.0,
    "voltage_kv": 220.0,
}


def test_list_components_manager(client):
    login(client)
    response = client.get("/components")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_list_components_user(client):
    login(client, username="user", password="userpass")
    response = client.get("/components")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_list_components_not_authenticated(client):
    # no login
    response = client.get("/components")
    assert response.status_code == 401


def test_list_components_filter_by_type(client):
    login(client)
    response = client.get("/components?component_type=transformer")
    assert response.status_code == 200

    data = response.json()
    assert all(component["component_type"] == "transformer" for component in data)


def test_list_components_filter_by_substation(client):
    login(client)
    response = client.get("/components?substation=S2")
    assert response.status_code == 200

    data = response.json()
    assert all(component["substation"] == "S2" for component in data)


def test_create_component_manager(client):
    login(client)
    payload = COMPONENT.copy()

    response = client.post("/components", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "T-new"
    assert data["component_type"] == "transformer"
    assert "id" in data


def test_create_component_user(client):
    login(client, username="user", password="userpass")
    payload = COMPONENT.copy()

    response = client.post("/components", json=payload)
    assert response.status_code == 403


def test_create_component_not_authenticated(client):
    payload = COMPONENT.copy()

    response = client.post("/components", json=payload)
    assert response.status_code == 401


def test_create_component_invalid_payload(client):
    login(client)
    # missing capacity_mva
    payload = {
        "component_type": "transformer",
        "name": "BROKEN",
        "substation": "S1",
        "voltage_kv": 132.0,
    }

    response = client.post("/components", json=payload)
    assert response.status_code == 422


def test_update_component(client):
    login(client)
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    update_payload = UPDATE_COMPONENT.copy()

    response = client.put(f"/components/{component_id}", json=update_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "T-updated"
    assert data["capacity_mva"] == 150.0
    assert data["voltage_kv"] == 220.0


def test_update_component_not_authorized(client):
    login(client, username="user", password="userpass")
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    update_payload = UPDATE_COMPONENT.copy()

    response = client.put(f"/components/{component_id}", json=update_payload)
    assert response.status_code == 403


def test_update_component_not_authenticated(client):
    login(client, username="user", password="userpass")
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    update_payload = UPDATE_COMPONENT.copy()

    logout(client)
    response = client.put(f"/components/{component_id}", json=update_payload)
    assert response.status_code == 401


def test_update_component_not_found(client):
    login(client)
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
    login(client)
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    # changing type
    payload = {
        "component_type": "line",
        "name": "L-hacker",
        "substation": "S1",
        "length_km": 10.0,
        "voltage_kv": 132.0,
    }

    response = client.put(f"/components/{component_id}", json=payload)
    assert response.status_code == 409


def test_update_component_missing_type(client):
    login(client)
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    payload = {
        "name": "NO-TYPE",
        "substation": "S1",
        "capacity_mva": 99.0,
        "voltage_kv": 132.0,
    }

    response = client.put(f"/components/{component_id}", json=payload)
    assert response.status_code == 422


def test_delete_componet(client):
    login(client)
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    response = client.delete(f"/components/{component_id}")
    assert response.status_code == 204

    # veryfing it is deleted
    response = client.get("/components?component_type=transformer")
    ids = [x["id"] for x in response.json()]
    assert component_id not in ids


def test_delete_componet_not_authorized(client):
    login(client, username="user", password="userpass")
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    response = client.delete(f"/components/{component_id}")
    assert response.status_code == 403

    # veryfing it is not deleted
    response = client.get("/components?component_type=transformer")
    ids = [x["id"] for x in response.json()]
    assert component_id in ids


def test_delete_componet_not_authenticated(client):
    login(client)
    response = client.get("/components?component_type=transformer&limit=1&offset=0")
    component_id = response.json()[0]["id"]

    logout(client)

    response = client.delete(f"/components/{component_id}")
    assert response.status_code == 401

    # veryfing it is not deleted
    login(client)
    response = client.get("/components?component_type=transformer")
    ids = [x["id"] for x in response.json()]
    assert component_id in ids


def test_delete_component_not_found(client):
    login(client)
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/components/{fake_id}")
    assert response.status_code == 404
