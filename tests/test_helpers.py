"""Unit tests for private helper functions in src/api/endpoints/auth.py."""

from datetime import timedelta

import jwt

from src.api.endpoints.auth import _create_token, _hash_password, _verify_password

TEST_SECRET_KEY = "test-secret-key-for-unit-tests-at-least-32b"


# ---------------------------------------------------------------------------
# _hash_password
# ---------------------------------------------------------------------------


def test_hash_password_returns_bcrypt_hash():
    hashed = _hash_password("mypassword")
    assert hashed.startswith("$2b$")


def test_hash_password_returns_string():
    hashed = _hash_password("mypassword")
    assert isinstance(hashed, str)


def test_hash_password_different_calls_produce_different_hashes():
    hash1 = _hash_password("mypassword")
    hash2 = _hash_password("mypassword")
    assert hash1 != hash2


# ---------------------------------------------------------------------------
# _verify_password
# ---------------------------------------------------------------------------


def test_verify_password_returns_true_for_correct_password():
    hashed = _hash_password("correct-horse-battery")
    assert _verify_password("correct-horse-battery", hashed) is True


def test_verify_password_returns_false_for_wrong_password():
    hashed = _hash_password("correct-horse-battery")
    assert _verify_password("wrong-password", hashed) is False


# ---------------------------------------------------------------------------
# _create_token
# ---------------------------------------------------------------------------


def test_create_token_returns_string():
    token = _create_token({"sub": "42"}, timedelta(minutes=15))
    assert isinstance(token, str)


def test_create_token_contains_expected_payload():
    token = _create_token({"sub": "42", "email": "user@example.com"}, timedelta(minutes=15))
    decoded = jwt.decode(token, TEST_SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == "42"
    assert decoded["email"] == "user@example.com"


def test_create_token_contains_exp_claim():
    token = _create_token({"sub": "42"}, timedelta(minutes=15))
    decoded = jwt.decode(token, TEST_SECRET_KEY, algorithms=["HS256"])
    assert "exp" in decoded


def test_create_token_expired_raises_on_decode():
    token = _create_token({"sub": "99"}, timedelta(seconds=-1))
    try:
        jwt.decode(token, TEST_SECRET_KEY, algorithms=["HS256"])
        assert False, "Expected ExpiredSignatureError was not raised"
    except jwt.ExpiredSignatureError:
        pass
