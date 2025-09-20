import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func
from typing import AsyncGenerator
import logging
from ..models import *  # noqa

from .settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.database_min_connections,
    max_overflow=settings.database_max_connections - settings.database_min_connections,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


class TimestampMixin:
    """Mixin for models that need created_at and updated_at timestamps"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")