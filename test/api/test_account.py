from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.sql.account_sql import get_account_by_username


class TestAccount:
    existing_account_id: str = "D18CB2F2-9D03-4169-AC4D-0D9DB20E3D32"
    existing_email: str = "test@test.ai"
    existing_role_id1: int = 1
    existing_role_id2: int = 2
    existing_organization_id: int = 1
    existing_username: str = "test_user"
    existing_title: str = "engineer"

    @classmethod
    def __change_attr_cls(cls, name, value):
        setattr(cls, name, value)

    def generate_test_account(self):
        return {
            "username": str(uuid4()),
            "email": str(uuid4()) + "@example.com",
            "organization_id": self.existing_organization_id,
            "role_id": self.existing_role_id2,
            "password": "1234",
        }

    def test_add_account(self, client: TestClient, headers) -> None:
        response = client.post("/account/", json=self.generate_test_account(), headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "account_id" in content.keys()
        assert isinstance(content["account_id"], str)

    def test_list_accounts(self, client: TestClient, headers) -> None:
        response = client.get("/account/", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "account" in content.keys()
        assert isinstance(content["account"], list)

        # accounts was ordered by last_update field, then must be the recently add account
        accounts = list(content["account"])
        assert len(accounts) >= 2
        assert any(a["username"] == self.existing_username for a in accounts)

    def test_get_account(self, client: TestClient, headers) -> None:
        response = client.get(f"/account/{self.existing_account_id}", headers=headers)
        assert response.status_code == 200
        content = response.json()
        assert "account" in content.keys()
        assert (
            content["account"]["username"] == self.existing_username
            and content["account"]["email"] == self.existing_email
            and content["account"]["role_id"] == self.existing_role_id1
            and content["account"]["job_title"] == self.existing_title
        )

    def test_get_fake_account(self, client: TestClient, headers) -> None:
        response = client.get("/account/0", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "error" in content.keys()
        assert content["error"] == "account_id not valid"

    def test_update_account(self, client: TestClient, headers) -> None:
        # Arrange
        account = self.generate_test_account()
        response = client.post("/account/", json=account, headers=headers)
        content = response.json()
        response = client.put(f"/account/{content['account_id']}", json={"job_title": "employee"}, headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "account" in content.keys()
        assert (
            content["account"]["username"] == account["username"]
            and content["account"]["email"] == account["email"]
            and content["account"]["role_id"] == account["role_id"]
            and content["account"]["job_title"] == "employee"
            and content["account"]["organization_id"] == account["organization_id"]
        )

    def test_delete_account(self, client: TestClient, headers, sql_db: Session) -> None:
        response = client.delete(f"/account/{self.existing_account_id}", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "account" in content.keys()
        assert content["account"] == "deleted 1 rows"

        assert response.status_code == 200
        assert get_account_by_username(sql_db, self.existing_username) is None  # Check it was deleted

    def test_delete_fake_account(self, client: TestClient, headers) -> None:
        response = client.delete("/account/0", headers=headers)

        assert response.status_code == 200

        content = response.json()
        assert "error" in content.keys()
        assert content["error"] == "error, account_id: 0 don't exists"
