"""Database configuration and session management.

This module provides SQLAlchemy setup for async database operations
following clean architecture principles.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# Database URL - using environment configuration
# For local development, use the DATABASE_URL from environment
# For production, this would be the Supabase connection string
DATABASE_URL = getattr(settings, "database_url", None)

# Ensure we use asyncpg driver for async operations
if DATABASE_URL:
    # Replace postgresql:// with postgresql+asyncpg:// if needed
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    # Fallback to constructing from individual components
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.log_level.lower() == "debug",
    future=True,
)

# Create session factory
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
