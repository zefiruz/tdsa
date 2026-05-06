import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from faker import Faker
from app.main import app, db

fake = Faker()

@pytest_asyncio.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
def clean_db():
    # Очистка базы (словаря) перед каждым тестом (Изоляция состояния)
    db.clear()
    
    # Сброс счетчика ID
    import itertools
    from app import main
    main._id_seq = itertools.count(start=1)
    yield

@pytest.fixture
def fake_user_data():
    return {
        "username": fake.user_name(),
        "age": fake.random_int(min=1, max=100)
    }