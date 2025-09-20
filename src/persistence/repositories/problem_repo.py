from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from src.models.problem import ProblemStatementCreate, ProblemStatementUpdate
from .base_repo import BaseRepository
from .user_repo import ProblemStatementORM


class ProblemRepository(BaseRepository[ProblemStatementORM, ProblemStatementCreate, ProblemStatementUpdate]):
    """Problem statement repository with specialized methods"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ProblemStatementORM)
    
    async def create_for_user(self, obj_in: ProblemStatementCreate, user_id: UUID) -> ProblemStatementORM:
        """Create problem for a specific user"""
        obj_data = obj_in.model_dump()
        obj_data['user_id'] = user_id  # Add user_id from authentication
        
        db_obj = ProblemStatementORM(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get_by_id_and_user(self, problem_id: UUID, user_id: UUID) -> Optional[ProblemStatementORM]:
        """Get problem by ID and user ID"""
        result = await self.db.execute(
            select(ProblemStatementORM).where(
                and_(
                    ProblemStatementORM.id == problem_id,
                    ProblemStatementORM.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_user(
        self, 
        user_id: UUID, 
        page: int = 1, 
        size: int = 10,
        problem_type: Optional[str] = None
    ) -> Tuple[List[ProblemStatementORM], int]:
        """List problems by user with pagination and filtering"""
        conditions = [ProblemStatementORM.user_id == user_id]
        
        if problem_type:
            conditions.append(ProblemStatementORM.problem_type == problem_type)
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count(ProblemStatementORM.id)).where(and_(*conditions))
        )
        total = count_result.scalar()
        
        # Get paginated results
        offset = (page - 1) * size
        result = await self.db.execute(
            select(ProblemStatementORM)
            .where(and_(*conditions))
            .offset(offset)
            .limit(size)
            .order_by(ProblemStatementORM.created_at.desc())
        )
        
        problems = result.scalars().all()
        return problems, total