"""Integration tests for all auth endpoints."""

from datetime import timedelta

from src.api.endpoints.auth import _create_token

TEST_SECRET_KEY = "test-secret-key-for-unit-tests-at-least-32b"


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------


def test_register_success(client):
    r = client.post("/register", json={"email": "new@example.com", "password": "password123"})
    assert r.status_code == 201
    assert r.json() == {"ok": True}


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "password123"}
    client.post("/register", json=payload)
    r = client.post("/register", json=payload)
    assert r.status_code == 409


def test_register_invalid_email(client):
    r = client.post("/register", json={"email": "not-an-email", "password": "password123"})
    assert r.status_code == 422


def test_register_password_too_short(client):
    r = client.post("/register", json={"email": "short@example.com", "password": "abc"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------


def test_login_success(client, registered_user):
    r = client.post("/login", json=registered_user)
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_login_sets_cookies(client, registered_user):
    r = client.post("/login", json=registered_user)
    assert "access_token" in r.cookies
    assert "refresh_token" in r.cookies


def test_login_wrong_password(client, registered_user):
    r = client.post("/login", json={"email": registered_user["email"], "password": "wrongpassword"})
    assert r.status_code == 401


def test_login_unknown_email(client):
    r = client.post("/login", json={"email": "ghost@example.com", "password": "password123"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# POST /refresh
# ---------------------------------------------------------------------------


def test_refresh_success(authenticated_client):
    r = authenticated_client.post("/refresh")
    assert r.status_code == 200
    assert r.json() == {"ok": True}
    assert "access_token" in r.cookies


def test_refresh_no_cookie(client):
    r = client.post("/refresh")
    assert r.status_code == 401


def test_refresh_expired_token(client, registered_user):
    expired = _create_token({"sub": "1"}, timedelta(seconds=-1))
    client.cookies.set("refresh_token", expired)
    r = client.post("/refresh")
    assert r.status_code == 401


def test_refresh_tampered_token(client):
    client.cookies.set("refresh_token", "this.is.not.a.valid.token")
    r = client.post("/refresh")
    assert r.status_code == 401


def test_refresh_user_not_found(client):
    token = _create_token({"sub": "99999"}, timedelta(days=7))
    client.cookies.set("refresh_token", token)
    r = client.post("/refresh")
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------


def test_logout_success(authenticated_client):
    r = authenticated_client.post("/logout")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_logout_clears_cookies(authenticated_client):
    authenticated_client.post("/logout")
    r = authenticated_client.get("/me")
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------


def test_me_success(authenticated_client, registered_user):
    r = authenticated_client.get("/me")
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == registered_user["email"]
    assert "id" in body


def test_me_no_cookie(client):
    r = client.get("/me")
    assert r.status_code == 401


def test_me_expired_token(client, registered_user):
    expired = _create_token({"sub": "1", "email": registered_user["email"]}, timedelta(seconds=-1))
    client.cookies.set("access_token", expired)
    r = client.get("/me")
    assert r.status_code == 401


def test_me_tampered_token(client):
    client.cookies.set("access_token", "tampered.token.value")
    r = client.get("/me")
    assert r.status_code == 401


def test_me_user_not_found(client):
    token = _create_token({"sub": "99999", "email": "ghost@example.com"}, timedelta(minutes=15))
    client.cookies.set("access_token", token)
    r = client.get("/me")
    assert r.status_code == 401
