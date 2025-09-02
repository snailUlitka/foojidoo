from __future__ import annotations
from types import SimpleNamespace

import pytest

from api.dependencies import get_db, get_settings
from api.routers import auth


class DummyUser:
    def __init__(self, user_id: int, username: str, password: str) -> None:
        self.user_id = user_id
        self.username = username
        self.password = password


class DummyUserRepo:
    def __init__(self, users: list[DummyUser]) -> None:
        self.users = {u.username: u for u in users}

    def get_by_username(self, username: str) -> DummyUser | None:
        return self.users.get(username)

    def verify_password(self, plain: str, stored: str) -> bool:
        return plain == stored


class DummyTokenRepo:
    def __init__(self) -> None:
        self.tokens: dict[int, set[str]] = {}

    def add_refresh_token(self, user_id: int, token: str, expiry: int) -> None:
        self.tokens.setdefault(user_id, set()).add(token)

    def is_refresh_token_valid(self, user_id: int, token: str) -> bool:
        return token in self.tokens.get(user_id, set())

    def revoke_refresh_token(self, user_id: int, token: str) -> None:
        self.tokens.get(user_id, set()).discard(token)


@pytest.fixture
def setup_auth(client, monkeypatch: pytest.MonkeyPatch):
    user = DummyUser(1, "alice", "pw")
    user_repo = DummyUserRepo([user])
    token_repo = DummyTokenRepo()

    monkeypatch.setattr(auth, "UserRepository", lambda db: user_repo)
    monkeypatch.setattr(auth, "TokenRepository", lambda db: token_repo)
    monkeypatch.setattr(auth, "create_tokens", lambda uid, settings: ("access", "refresh", 0))

    def fake_verify(token: str, settings) -> dict[str, str]:
        if token in {"refresh", "old", "ref"}:
            return {"sub": "1"}
        raise Exception("bad token")

    monkeypatch.setattr(auth, "verify_token", fake_verify)

    client.app.dependency_overrides[get_db] = lambda: None
    client.app.dependency_overrides[get_settings] = lambda: SimpleNamespace(access_token_expire_minutes=1)
    return client, token_repo


def test_login_success(setup_auth) -> None:
    client, token_repo = setup_auth
    response = client.post("/auth/login", data={"username": "alice", "password": "pw"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "access"
    assert token_repo.is_refresh_token_valid(1, "refresh")


def test_login_invalid_credentials(setup_auth) -> None:
    client, _ = setup_auth
    response = client.post("/auth/login", data={"username": "alice", "password": "wrong"})
    assert response.status_code == 401


def test_refresh_success(setup_auth, monkeypatch: pytest.MonkeyPatch) -> None:
    client, token_repo = setup_auth
    token_repo.add_refresh_token(1, "old", 0)
    monkeypatch.setattr(auth, "create_tokens", lambda uid, settings: ("new_access", "new_refresh", 0))
    response = client.post("/auth/refresh", json={"refresh_token": "old"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "new_access"
    assert token_repo.is_refresh_token_valid(1, "new_refresh")


def test_refresh_invalid_token(setup_auth, monkeypatch: pytest.MonkeyPatch) -> None:
    client, _ = setup_auth
    monkeypatch.setattr(auth, "verify_token", lambda token, settings: (_ for _ in ()).throw(Exception("bad")))
    response = client.post("/auth/refresh", json={"refresh_token": "bad"})
    assert response.status_code == 401


def test_logout_success(setup_auth) -> None:
    client, token_repo = setup_auth
    token_repo.add_refresh_token(1, "ref", 0)
    response = client.post("/auth/logout", json={"refresh_token": "ref"})
    assert response.status_code == 200
    assert not token_repo.is_refresh_token_valid(1, "ref")


def test_logout_invalid_token(setup_auth, monkeypatch: pytest.MonkeyPatch) -> None:
    client, _ = setup_auth
    monkeypatch.setattr(auth, "verify_token", lambda token, settings: (_ for _ in ()).throw(Exception("bad")))
    response = client.post("/auth/logout", json={"refresh_token": "bad"})
    assert response.status_code == 401
