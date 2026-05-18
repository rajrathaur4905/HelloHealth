"""
Test Configuration and Shared Fixtures.

Provides the foundational test infrastructure for the HelloHealth backend:
  - Async SQLite test database (no PostgreSQL dependency in CI)
  - Overridden FastAPI dependency injection for database sessions
  - Async HTTP test client via httpx
  - Auth helper fixture (register a user + get JWT token)

Usage:
    All fixtures are auto-discovered by pytest from this file.

    async def test_something(client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import create_app

# ── Test Database ────────────────────────────────────────────
# Use async SQLite so tests run without Docker/PostgreSQL.
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Database Override ────────────────────────────────────────

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session and handle cleanup."""
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── App Fixture ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def anyio_backend():
    """Tell pytest-asyncio to use asyncio (not trio)."""
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop them after.

    This ensures every test starts with a clean database state.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client with dependency overrides.

    The test client speaks directly to the ASGI app — no network
    calls are made. Database dependency is overridden to use the
    test SQLite database.
    """
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clear overrides after the test
    app.dependency_overrides.clear()


# ── Auth Helper Fixture ──────────────────────────────────────

@pytest.fixture
async def auth_token(client: AsyncClient) -> str:
    """Register a test user and return a valid JWT access token.

    Creates a user with known credentials and returns the token
    for use in authenticated endpoint tests.
    """
    register_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPass123",
    }
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201, f"Registration failed: {response.text}"
    return response.json()["data"]["access_token"]
