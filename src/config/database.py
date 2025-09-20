import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func
import logging

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
    future=True,  # Add this
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
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
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise



async def init_database():
    """Initialize database tables"""
    try:
        # Import all ORM models to ensure they're registered
        from ..persistence.repositories.user_repo import Base as UserBase
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(UserBase.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")