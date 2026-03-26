import os

# MUST be set BEFORE any src imports — modules execute at import time
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-tests-at-least-32b"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.app import app
from src.api.database import Base, get_db

TEST_SECRET_KEY = "test-secret-key-for-unit-tests-at-least-32b"
TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    client.post("/register", json={"email": "user@example.com", "password": "password123"})
    return {"email": "user@example.com", "password": "password123"}


@pytest.fixture
def authenticated_client(client, registered_user):
    client.post("/login", json=registered_user)
    return client
