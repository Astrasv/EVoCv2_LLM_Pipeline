from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import declarative_base

from src.models.user import UserCreate, UserUpdate
from src.utils.security import get_password_hash
from .base_repo import BaseRepository

# SQLAlchemy ORM models
Base = declarative_base()

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, JSON, ARRAY, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid


class UserORM(Base):
    __tablename__ = "users"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    subscription_tier = Column(String(20), default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    problems = relationship("ProblemStatementORM", back_populates="user", cascade="all, delete-orphan")


class ProblemStatementORM(Base):
    __tablename__ = "problem_statements"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    problem_type = Column(String(50), nullable=False)
    constraints = Column(JSON, default={})
    objectives = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserORM", back_populates="problems")
    notebooks = relationship("NotebookORM", back_populates="problem", cascade="all, delete-orphan")


class NotebookORM(Base):
    __tablename__ = "notebooks"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(PGUUID(as_uuid=True), ForeignKey("problem_statements.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    deap_toolbox_config = Column(JSON, default={})
    status = Column(String(20), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    problem = relationship("ProblemStatementORM", back_populates="notebooks")
    cells = relationship("NotebookCellORM", back_populates="notebook", cascade="all, delete-orphan")


class NotebookCellORM(Base):
    __tablename__ = "notebook_cells"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notebook_id = Column(PGUUID(as_uuid=True), ForeignKey("notebooks.id", ondelete="CASCADE"))
    cell_type = Column(String(20), nullable=False)
    code = Column(Text, default="")
    agent_id = Column(String(50))
    version = Column(Integer, default=1)
    position = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    notebook = relationship("NotebookORM", back_populates="cells")


class UserRepository(BaseRepository[UserORM, UserCreate, UserUpdate]):
    """User repository with specialized methods"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserORM)
    
    async def get_by_email(self, email: str) -> Optional[UserORM]:
        """Get user by email"""
        result = await self.db.execute(
            select(UserORM).where(UserORM.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[UserORM]:
        """Get user by username"""
        result = await self.db.execute(
            select(UserORM).where(UserORM.username == username)
        )
        return result.scalar_one_or_none()
    
    async def create(self, obj_in: UserCreate) -> UserORM:
        """Create new user with password hashing"""
        obj_data = obj_in.model_dump()
        # Hash password
        password = obj_data.pop('password')  # Remove plain password
        obj_data['password_hash'] = get_password_hash(password)  # Add hashed password
        
        db_obj = UserORM(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: UUID, obj_in: UserUpdate) -> Optional[UserORM]:
        """Update user with optional password hashing"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        # Handle password update
        if 'password' in obj_data:
            password = obj_data.pop('password')
            obj_data['password_hash'] = get_password_hash(password)
        
        if not obj_data:
            return await self.get_by_id(id)
        
        from sqlalchemy import update
        stmt = (
            update(UserORM)
            .where(UserORM.id == id)
            .values(**obj_data)
            .returning(UserORM)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

