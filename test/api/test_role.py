from uuid import uuid4

from fastapi.testclient import TestClient


class TestRole:
    role_name: str = str(uuid4())
    role_id: int = 0

    @classmethod
    def __change_role_id(cls, role_id):
        cls.role_id = role_id

    def test_add_role(self, client: TestClient, headers) -> None:
        response = client.post("/role/", json={"name": self.role_name}, headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "role_id" in content.keys()
        assert isinstance(content["role_id"], int)
        TestRole.__change_role_id(content["role_id"])

    def test_list_roles(self, client: TestClient, headers) -> None:
        response = client.get("/role/", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "roles" in content.keys()
        assert isinstance(content["roles"], list)

        for role in content["roles"]:
            if role["name"] == self.role_name:
                break
        else:
            assert False, "role was not added"

    def test_get_role(self, client: TestClient, headers) -> None:
        response = client.get(f"/role/{self.role_id}", headers=headers)
        assert response.status_code == 200

        content = response.json()
        assert "role" in content.keys()
        assert content["role"]["name"] == self.role_name

    def test_get_fakerole(self, client: TestClient, headers) -> None:
        response = client.get("/role/0", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "error" in content.keys()
        assert content["error"] == "role_id: 0 not valid"

    def test_delete_role(self, client: TestClient, headers) -> None:
        response = client.delete(f"/role/{self.role_id}", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "role" in content.keys()
        assert content["role"] == "deleted 1 rows"

    def test_delete_fake_role(self, client: TestClient, headers) -> None:
        response = client.delete("/role/0", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "error" in content.keys()
        assert content["error"] == "error, role_id: 0 don't exists"
