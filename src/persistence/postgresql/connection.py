import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import logging

from src.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.engine: AsyncEngine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connections"""
        try:
            self.engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                pool_size=settings.database_min_connections,
                max_overflow=settings.database_max_connections - settings.database_min_connections,
                pool_pre_ping=True,
                pool_recycle=3600,
                poolclass=NullPool if "sqlite" in settings.database_url else None
            )
            
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            
            logger.info("Database manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if not self.session_factory:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session"""
    async for session in db_manager.get_session():
        yield session