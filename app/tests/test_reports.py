from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.tests.auth import login, logout


def test_post_report(client):
    login(client)

    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=3)

    report = {
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
    }

    response = client.post("/reports", json=report)
    assert response.status_code == 202

    data = response.json()

    assert "id" in data
    assert data["status"] == "PENDING"


def test_post_report_not_authorized(client):
    login(client, username="user", password="userpass")

    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=3)

    report = {
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
    }

    response = client.post("/reports", json=report)
    assert response.status_code == 403


def test_post_report_not_authenticated(client):

    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=3)

    report = {
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
    }

    response = client.post("/reports", json=report)
    assert response.status_code == 401



def test_post_report_invalid_from_to_date(client):
    login(client)

    from_date = datetime.now(timezone.utc)
    to_date = from_date - timedelta(days=3)

    report = {
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
    }

    response = client.post("/reports", json=report)
    assert response.status_code == 400
