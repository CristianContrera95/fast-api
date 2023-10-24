from fastapi.testclient import TestClient


def test_header(
    client: TestClient,
) -> None:
    response = client.get("/", headers={"Host": "localhost"})
    assert response.status_code == 200
    content = response.json()
    assert content["Hello"] == "Api is alive"
