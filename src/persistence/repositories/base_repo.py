from typing import TypeVar, Generic, Optional, List, Type, Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=declarative_base())
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination"""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create new entity"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update entity by ID"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        if not obj_data:
            return await self.get_by_id(id)
        
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_data)
            .returning(self.model)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0
    
    async def count(self) -> int:
        """Count total entities"""
        result = await self.db.execute(
            select(func.count(self.model.id))
        )
        return result.scalar()