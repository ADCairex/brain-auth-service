import os

# MUST be set BEFORE any src imports — modules execute at import time
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-tests-at-least-32b"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
