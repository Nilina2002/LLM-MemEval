"""
Async database session factory.
Switching from SQLite to PostgreSQL requires only changing DATABASE_URL in .env.
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    # SQLite: allow multiple connections (needed for background tasks)
    connect_args={"timeout": 30, "check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL
    else {},
)

# Enable WAL mode for SQLite — allows one writer + multiple readers concurrently
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for database sessions with automatic rollback on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create all tables defined in ORM models. Called at application startup."""
    from app.database.base import Base
    import app.models  # noqa: F401 — import all models to register them with Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
