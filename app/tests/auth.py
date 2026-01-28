from __future__ import annotations


def login(client, username: str = "manager", password: str = "managerpass") -> str:
    """
    perform a real login via using /token endpoint and set authorization header on the client.
    default UserRole is 'manager'.
    returns the access token.
    """
    response = client.post(
        "/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return token


def logout(client) -> None:
    """
    remove authorization header from the client.
    """
    client.headers.pop("Authorization", None)

