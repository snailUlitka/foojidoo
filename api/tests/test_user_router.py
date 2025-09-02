from __future__ import annotations
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient
import pytest

from api.main import app
from api.dependencies import get_current_user, get_order_repo, get_user_repo


class DummyUser:
    def __init__(self, user_id: int, name: str, phone: str, address: str, password: str = "pwd") -> None:
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.address = address
        self.password = password


class DummyUserRepo:
    def __init__(self, existing: list[DummyUser] | None = None) -> None:
        self.users = {u.name: u for u in existing or []}

    def get_by_username(self, username: str) -> DummyUser | None:
        return self.users.get(username)

    def create_user(self, username: str, password: str, phone: str, address: str) -> DummyUser:
        user_id = len(self.users) + 1
        user = DummyUser(user_id, username, phone, address, password)
        self.users[username] = user
        return user

    def update_user(self, user: DummyUser, **fields: str | None) -> DummyUser:
        for attr, val in fields.items():
            if val is not None:
                setattr(user, attr, val)
        return user

    def delete_user(self, user: DummyUser) -> None:
        self.users.pop(user.name, None)


class DummyOrderRepo:
    def create_order(self, user: DummyUser) -> object:
        self.created_for = user.user_id
        return object()


@pytest.fixture
def client_and_repo() -> tuple[TestClient, DummyUserRepo]:
    user_repo = DummyUserRepo()
    order_repo = DummyOrderRepo()
    app.dependency_overrides[get_user_repo] = lambda: user_repo
    app.dependency_overrides[get_order_repo] = lambda: order_repo
    with TestClient(app) as client:
        yield client, user_repo
    app.dependency_overrides.clear()


def test_create_user_success(client_and_repo: tuple[TestClient, DummyUserRepo]) -> None:
    client, _ = client_and_repo
    payload = {"name": "alice", "password": "secretpw", "phone": "123", "address": "street"}
    response = client.post("/user/users/", json=payload)
    assert response.status_code == 201
    assert response.json() == {
        "user_id": 1,
        "name": "alice",
        "phone": "123",
        "address": "street",
    }


def test_create_user_duplicate(client_and_repo: tuple[TestClient, DummyUserRepo]) -> None:
    client, repo = client_and_repo
    repo.users["bob"] = DummyUser(1, "bob", "555", "addr")
    payload = {"name": "bob", "password": "secret", "phone": "123", "address": "addr"}
    response = client.post("/user/users/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this name already exists"


def test_read_own_profile(client_and_repo: tuple[TestClient, DummyUserRepo]) -> None:
    client, _ = client_and_repo
    user = DummyUser(1, "carol", "789", "main")
    client.app.dependency_overrides[get_current_user] = lambda: user
    response = client.get("/user/users/me")
    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "name": "carol",
        "phone": "789",
        "address": "main",
    }
    client.app.dependency_overrides.pop(get_current_user, None)


def test_update_profile(client_and_repo: tuple[TestClient, DummyUserRepo]) -> None:
    client, _ = client_and_repo
    user = DummyUser(1, "dave", "111", "old")
    client.app.dependency_overrides[get_current_user] = lambda: user
    payload = {"phone": "222", "address": "new"}
    response = client.put("/user/users/me", json=payload)
    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "name": "dave",
        "phone": "222",
        "address": "new",
    }
    client.app.dependency_overrides.pop(get_current_user, None)


def test_update_profile_partial(client_and_repo: tuple[TestClient, DummyUserRepo]) -> None:
    client, _ = client_and_repo
    user = DummyUser(1, "erin", "333", "home")
    client.app.dependency_overrides[get_current_user] = lambda: user
    payload = {"address": "office"}
    response = client.put("/user/users/me", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "office"
    assert data["phone"] == "333"
    client.app.dependency_overrides.pop(get_current_user, None)


def test_delete_profile(client_and_repo: tuple[TestClient, DummyUserRepo]) -> None:
    client, repo = client_and_repo
    user = DummyUser(1, "frank", "444", "place")
    client.app.dependency_overrides[get_current_user] = lambda: user
    response = client.delete("/user/users/me")
    assert response.status_code == 204
    assert "frank" not in repo.users
    client.app.dependency_overrides.pop(get_current_user, None)
