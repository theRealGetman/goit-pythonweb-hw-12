import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.services.redis import get_redis_service
from src.db.models.base import Base
from src.db.models.user import User
from main import app
from src.db.db import get_db
from src.services.auth import create_access_token, Hash


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}


# Mock Redis service
class MockRedisService:
    def __init__(self):
        self.cache = {}

    async def get(self, key):
        return self.cache.get(key)

    async def set(self, key, value, expire=None):
        self.cache[key] = value

    async def delete(self, key):
        if key in self.cache:
            del self.cache[key]

    async def flush(self):
        self.cache.clear()


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                avatar="<https://twitter.com/gravatar>",
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override
    redis_service = MockRedisService()

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    def override_get_redis_service():
        return redis_service

    app.dependency_overrides[get_redis_service] = override_get_redis_service
    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app, client=("127.0.0.1", 50000))

    yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["username"]})
    return token
