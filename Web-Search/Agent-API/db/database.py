"""
Database configuration and connection management
"""
import os
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .models import Base

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./agent_api.db"
)

# Create async engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL logging
        future=True,
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL logging
        future=True,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=30,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections
    """
    await engine.dispose()