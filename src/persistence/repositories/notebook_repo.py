from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update, text
from sqlalchemy.orm import selectinload

from src.models.notebook import NotebookCreate, NotebookUpdate, NotebookCellUpdate
from .user_repo import NotebookORM, NotebookCellORM, ProblemStatementORM


class NotebookRepository:
    """Simplified notebook repository to fix async issues"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, notebook_data: NotebookCreate) -> NotebookORM:
        """Create new notebook"""
        # Convert Pydantic model to dict
        obj_data = notebook_data.model_dump()
        
        # Create ORM object
        db_obj = NotebookORM(**obj_data)
        
        # Add to session
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        
        return db_obj
    
    async def get_by_id_and_user(self, notebook_id: UUID, user_id: UUID) -> Optional[NotebookORM]:
        """Get notebook by ID and user ID (through problem ownership)"""
        stmt = (
            select(NotebookORM)
            .join(ProblemStatementORM)
            .where(
                and_(
                    NotebookORM.id == notebook_id,
                    ProblemStatementORM.user_id == user_id
                )
            )
            .options(selectinload(NotebookORM.cells))
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_by_user(
        self, 
        user_id: UUID, 
        page: int = 1, 
        size: int = 10,
        status: Optional[str] = None
    ) -> Tuple[List[NotebookORM], int]:
        """List notebooks by user with pagination and filtering"""
        conditions = [ProblemStatementORM.user_id == user_id]
        
        if status:
            conditions.append(NotebookORM.status == status)
        
        # Get total count
        count_stmt = (
            select(func.count(NotebookORM.id))
            .join(ProblemStatementORM)
            .where(and_(*conditions))
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * size
        list_stmt = (
            select(NotebookORM)
            .join(ProblemStatementORM)
            .where(and_(*conditions))
            .offset(offset)
            .limit(size)
            .order_by(NotebookORM.created_at.desc())
            .options(selectinload(NotebookORM.cells))
        )
        
        result = await self.db.execute(list_stmt)
        notebooks = result.scalars().all()
        return notebooks, total
    
    async def update(self, notebook_id: UUID, notebook_update: NotebookUpdate) -> Optional[NotebookORM]:
        """Update notebook by ID"""
        obj_data = notebook_update.model_dump(exclude_unset=True)
        if not obj_data:
            # No updates, just return existing
            result = await self.db.execute(
                select(NotebookORM).where(NotebookORM.id == notebook_id)
            )
            return result.scalar_one_or_none()
        
        stmt = (
            update(NotebookORM)
            .where(NotebookORM.id == notebook_id)
            .values(**obj_data)
            .returning(NotebookORM)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete(self, notebook_id: UUID) -> bool:
        """Delete notebook by ID"""
        from sqlalchemy import delete
        stmt = delete(NotebookORM).where(NotebookORM.id == notebook_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0
    
    async def update_cell(self, cell_id: UUID, cell_update: NotebookCellUpdate) -> Optional[NotebookCellORM]:
        """Update a specific notebook cell"""
        obj_data = cell_update.model_dump(exclude_unset=True)
        if not obj_data:
            result = await self.db.execute(
                select(NotebookCellORM).where(NotebookCellORM.id == cell_id)
            )
            return result.scalar_one_or_none()
        
        stmt = (
            update(NotebookCellORM)
            .where(NotebookCellORM.id == cell_id)
            .values(**obj_data)
            .returning(NotebookCellORM)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()