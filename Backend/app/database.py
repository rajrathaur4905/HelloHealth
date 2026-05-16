"""
Database Engine and Session Management.

Provides the async SQLAlchemy engine, session factory, and a
FastAPI dependency (get_db) for injecting database sessions
into route handlers.

Usage in routers:
    from app.database import get_db

    @router.get("/items")
    async def list_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Item))
        return result.scalars().all()
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Async Engine ─────────────────────────────────────────────
# Creates a connection pool to PostgreSQL.
# pool_size=5:  maintain 5 persistent connections
# max_overflow=10: allow up to 10 extra connections under load
# echo: log SQL statements when DEBUG is enabled
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
)

# ── Session Factory ──────────────────────────────────────────
# Creates new AsyncSession instances bound to the engine.
# expire_on_commit=False: objects remain usable after commit
# (avoids lazy-load issues in async context)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative Base ─────────────────────────────────────────
# All SQLAlchemy ORM models inherit from this base class.
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ───────────────────────────────────────
# Yields a database session per request and ensures it is
# closed when the request completes (even on error).
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
