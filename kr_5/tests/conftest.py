import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    db.clear()