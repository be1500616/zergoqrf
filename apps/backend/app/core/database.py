"""Database configuration and session management.

This module provides SQLAlchemy setup for async database operations
following clean architecture principles.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


# ponytail: pool tuning deferred to load measurement. Add pool_size,
# max_overflow, pool_timeout only when a profiler says so.
engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level.lower() == "debug",
    future=True,
)

# Session factory bound to the engine above.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.

    Yields:
        AsyncSession: Database session for dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """Initialize database tables.

    Creates all tables defined in the Base metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    """Close database engine.

    Should be called on application shutdown.
    """
    await engine.dispose()
