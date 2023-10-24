from starlette.testclient import TestClient


def login(client: TestClient) -> str:
    response = client.post(
        "/token",
        data={"grant_type": "password", "username": "hello@marvik.ai", "password": 1, "scope": "*"},
        headers={"Content-Type": "application/x-www-form-urlencoded", "Host": "localhost"},
    )
    content = response.json()
    return content["access_token"]
